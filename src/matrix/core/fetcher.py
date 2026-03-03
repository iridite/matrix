"""RSS/Atom 抓取模块 - 物理截断防 API 暴走"""
import feedparser
from typing import List, Dict
from datetime import datetime


def fetch_feeds(feed_urls: List[str], max_items_per_feed: int = 10) -> List[Dict]:
    """
    从多个 RSS/Atom 源抓取最新条目

    Args:
        feed_urls: RSS/Atom URL 列表
        max_items_per_feed: 每个源最多抓取的条目数（物理截断）

    Returns:
        标准化的文章字典列表
    """
    articles = []

    for url in feed_urls:
        try:
            feed = feedparser.parse(url)

            # 物理截断：只取前 N 条
            for entry in feed.entries[:max_items_per_feed]:
                try:
                    article = {
                        "title": entry.get("title", "无标题"),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", entry.get("description", "")),
                        "published_date": entry.get("published", entry.get("updated", "")),
                        "source_url": url,
                    }
                    articles.append(article)
                except Exception as e:
                    print(f"⚠️  解析单条失败 [{url}]: {e}")
                    continue

        except Exception as e:
            print(f"❌ 抓取源失败 [{url}]: {e}")
            continue

    print(f"✅ 成功抓取 {len(articles)} 篇文章")
    return articles
