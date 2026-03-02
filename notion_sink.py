"""Notion 存储器 - 写入 Database"""
import os
import httpx
from typing import Optional
from datetime import datetime


def save_to_notion(
    article_output: dict,
    database_id: str,
    api_key: Optional[str] = None
) -> bool:
    """
    将生成的文章写入 Notion Database

    Args:
        article_output: ArticleOutput 的字典形式
        database_id: Notion Database ID
        api_key: Notion Integration Token

    Returns:
        是否成功
    """
    token = api_key or os.getenv("NOTION_API_KEY")
    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Notion API 数据结构
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "标题": {
                "title": [{"text": {"content": article_output["title"]}}]
            },
            "原文链接": {
                "url": article_output["original_url"]
            },
            "SEO标签": {
                "multi_select": [{"name": tag} for tag in article_output["seo_tags"]]
            },
            "创建时间": {
                "date": {"start": datetime.now().isoformat()}
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": article_output["content"][:2000]}}]
                }
            }
        ]
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print(f"✅ 已存入 Notion: {article_output['title']}")
            return True

    except Exception as e:
        print(f"❌ Notion 写入失败: {e}")
        return False
