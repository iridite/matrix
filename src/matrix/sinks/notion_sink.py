"""Notion 存储器 - 写入 Database"""
import os
import httpx
from typing import Optional


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

    # 构造页面内容块
    content_blocks = []

    # 添加原文链接（如果有）
    if article_output.get("original_url"):
        content_blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"原文: {article_output['original_url']}"}
                }]
            }
        })
        content_blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

    # 添加正文内容（分段处理，每段最多 2000 字符）
    content = article_output.get("content", "")
    paragraphs = content.split("\n\n")

    for para in paragraphs:
        if not para.strip():
            continue

        # Notion 单个 rich_text 限制 2000 字符
        chunks = [para[i:i+2000] for i in range(0, len(para), 2000)]
        for chunk in chunks:
            content_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": chunk}}]
                }
            })

    # 添加 SEO 标签（如果有）
    if article_output.get("seo_tags"):
        content_blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })
        tags_text = "标签: " + ", ".join(article_output["seo_tags"])
        content_blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": tags_text},
                    "annotations": {"italic": True, "color": "gray"}
                }]
            }
        })

    # Notion API 数据结构
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [{"text": {"content": article_output["title"]}}]
            }
        },
        "children": content_blocks
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
