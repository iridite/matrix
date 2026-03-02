"""手动输入源 - 支持直接输入文章内容"""
from typing import List, Dict
from datetime import datetime


def fetch_from_manual(title: str, content: str, link: str = "") -> List[Dict]:
    """
    手动输入单篇文章

    Args:
        title: 文章标题
        content: 文章内容
        link: 原文链接（可选）

    Returns:
        标准化的文章列表（单篇）
    """
    article = {
        "title": title,
        "link": link or "manual://input",
        "summary": content[:500],
        "published_date": datetime.now().isoformat(),
        "source_type": "manual",
        "content": content
    }

    return [article]
