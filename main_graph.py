"""Matrix 主流水线 - LangGraph 调度中心"""
import os
from dotenv import load_dotenv
from fetcher import fetch_feeds
from graph_builder import process_single_article

load_dotenv()

RSS_FEEDS = ["https://hnrss.org/frontpage", "https://www.reddit.com/r/programming/.rss"]
MAX_ITEMS = 5


def main():
    """主管道：使用 LangGraph 状态机处理文章"""
    print("🚀 Matrix [LangGraph]\n")

    # 抓取 RSS
    articles = fetch_feeds(RSS_FEEDS, max_items_per_feed=MAX_ITEMS)

    # 遍历处理每篇文章
    for idx, article in enumerate(articles, 1):
        try:
            # 执行状态机
            result = process_single_article(article)

            # 冷酷简短的日志
            if result.get("notion_url"):
                print(f"[{idx}] SUCCESS: {result['draft_title'][:50]}")
            elif result.get("error"):
                print(f"[{idx}] ERROR: {result['error']}")
            else:
                print(f"[{idx}] SKIP: {result.get('reason', 'N/A')}")

        except KeyboardInterrupt:
            print("\n[ABORT] 用户中断")
            break
        except Exception as e:
            print(f"[{idx}] FAIL: {str(e)}")
            continue

    print("\n✅ 完成")


if __name__ == "__main__":
    main()
