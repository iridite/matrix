"""RSS 源 - 从 RSS feeds 抓取文章"""
from typing import List, Dict
from fetcher import fetch_feeds


def fetch_from_rss(feed_urls: List[str], max_items: int = 5) -> List[Dict]:
    """
    从 RSS feeds 抓取文章

    Args:
        feed_urls: RSS feed URL 列表
        max_items: 每个 feed 最多抓取的文章数

    Returns:
        标准化的文章列表，每篇文章包含 source_type="rss"
    """
    articles = fetch_feeds(feed_urls, max_items_per_feed=max_items)

    # 添加 source_type 标记
    for article in articles:
        article["source_type"] = "rss"

    return articles
