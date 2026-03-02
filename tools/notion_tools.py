"""Notion 工具集 - 供 Agent 调用"""
import os
import httpx
from typing import List, Dict, Optional, Any


class NotionTools:
    """Notion 操作工具集"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"

    def search_pages(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        搜索 Notion 页面

        Args:
            query: 搜索关键词
            max_results: 最多返回结果数

        Returns:
            页面列表 [{"id": "xxx", "title": "xxx", "url": "xxx", "created_time": "xxx"}]
        """
        url = f"{self.base_url}/search"
        payload = {
            "query": query,
            "page_size": max_results,
            "filter": {"property": "object", "value": "page"}
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("results", []):
                    # 提取标题
                    title = "无标题"
                    if "properties" in item:
                        title_prop = item["properties"].get("title") or item["properties"].get("Name")
                        if title_prop and title_prop.get("title"):
                            title = title_prop["title"][0]["plain_text"]

                    results.append({
                        "id": item["id"],
                        "title": title,
                        "url": item.get("url", ""),
                        "created_time": item.get("created_time", "")
                    })

                return results

        except Exception as e:
            print(f"❌ Notion 搜索失败: {e}")
            return []

    def query_database(
        self,
        database_id: str,
        filter_dict: Optional[Dict[str, Any]] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        查询 Database 内容

        Args:
            database_id: Database ID
            filter_dict: 过滤条件（Notion API 格式）
            max_results: 最多返回结果数

        Returns:
            页面列表
        """
        url = f"{self.base_url}/databases/{database_id}/query"
        payload: Dict[str, Any] = {"page_size": max_results}

        if filter_dict:
            payload["filter"] = filter_dict

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("results", []):
                    # 提取所有属性
                    properties: Dict[str, Any] = {}
                    for key, value in item.get("properties", {}).items():
                        prop_type = value.get("type")
                        if prop_type == "title":
                            properties[key] = value["title"][0]["plain_text"] if value["title"] else ""
                        elif prop_type == "rich_text":
                            properties[key] = value["rich_text"][0]["plain_text"] if value["rich_text"] else ""
                        elif prop_type == "select":
                            properties[key] = value["select"]["name"] if value.get("select") else None
                        elif prop_type == "multi_select":
                            properties[key] = [s["name"] for s in value.get("multi_select", [])]
                        elif prop_type == "date":
                            properties[key] = value["date"]["start"] if value.get("date") else None
                        else:
                            properties[key] = str(value)

                    results.append({
                        "id": item["id"],
                        "url": item.get("url", ""),
                        "created_time": item.get("created_time", ""),
                        "properties": properties
                    })

                return results

        except Exception as e:
            print(f"❌ Database 查询失败: {e}")
            return []

    def get_page_content(self, page_id: str) -> str:
        """
        获取页面完整内容

        Args:
            page_id: 页面 ID

        Returns:
            页面内容（纯文本）
        """
        url = f"{self.base_url}/blocks/{page_id}/children"

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()

                content_parts = []
                for block in data.get("results", []):
                    block_type = block.get("type")
                    if block_type == "paragraph":
                        text = self._extract_rich_text(block["paragraph"]["rich_text"])
                        content_parts.append(text)
                    elif block_type == "heading_1":
                        text = self._extract_rich_text(block["heading_1"]["rich_text"])
                        content_parts.append(f"# {text}")
                    elif block_type == "heading_2":
                        text = self._extract_rich_text(block["heading_2"]["rich_text"])
                        content_parts.append(f"## {text}")
                    elif block_type == "heading_3":
                        text = self._extract_rich_text(block["heading_3"]["rich_text"])
                        content_parts.append(f"### {text}")
                    elif block_type == "bulleted_list_item":
                        text = self._extract_rich_text(block["bulleted_list_item"]["rich_text"])
                        content_parts.append(f"- {text}")

                return "\n\n".join(content_parts)

        except Exception as e:
            print(f"❌ 获取页面内容失败: {e}")
            return ""

    def check_duplicate(self, database_id: str, title: str) -> bool:
        """
        检查 Database 中是否已存在相似标题的页面

        Args:
            database_id: Database ID
            title: 要检查的标题

        Returns:
            是否存在重复
        """
        # 查询最近的页面
        results = self.query_database(database_id, max_results=50)

        # 简单的相似度检查
        title_lower = title.lower()
        for page in results:
            page_title = page["properties"].get("Name", "").lower()
            if title_lower in page_title or page_title in title_lower:
                return True

        return False

    def get_recent_topics(self, database_id: str, days: int = 7) -> List[str]:
        """
        获取最近发布的主题列表

        Args:
            database_id: Database ID
            days: 最近几天（暂未使用，返回最近 30 条）

        Returns:
            主题列表
        """
        results = self.query_database(database_id, max_results=30)

        topics = []
        for page in results:
            title = page["properties"].get("Name", "")
            if title:
                topics.append(title)

        return topics

    def _extract_rich_text(self, rich_text_array: List[Dict[str, Any]]) -> str:
        """提取 rich_text 数组的纯文本"""
        return "".join([item["plain_text"] for item in rich_text_array])


# 工具函数描述（供 Agent 理解）
NOTION_TOOLS_DESCRIPTION = """
可用的 Notion 工具：

1. search_pages(query: str) -> List[Dict]
   搜索 Notion 页面，返回匹配的页面列表

2. query_database(database_id: str, filter_dict: Dict = None) -> List[Dict]
   查询指定 Database 的内容，支持过滤条件

3. get_page_content(page_id: str) -> str
   获取页面的完整内容（纯文本格式）

4. check_duplicate(database_id: str, title: str) -> bool
   检查是否已存在相似标题的文章（避免重复发布）

5. get_recent_topics(database_id: str, days: int = 7) -> List[str]
   获取最近发布的主题列表（了解已覆盖的话题）

使用示例：
- 检查重复：check_duplicate(db_id, "AI 最新进展")
- 查看最近话题：get_recent_topics(db_id)
- 搜索相关内容：search_pages("机器学习")
"""
