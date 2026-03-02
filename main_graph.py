"""Matrix 主流水线 - LangGraph 多源输入调度中心"""
import os
from dotenv import load_dotenv
from graph_builder import process_single_article
from sources.rss_source import fetch_from_rss
from sources.note_source import fetch_from_notes

load_dotenv()


def main():
    """主管道：多源输入 -> LangGraph 状态机处理"""
    print("🚀 Matrix [多源输入 + LangGraph]\n")

    # 收集所有输入源
    articles = []

    # 1. RSS 源
    rss_feeds = os.getenv("RSS_FEEDS", "").split(",")
    if rss_feeds and rss_feeds[0]:
        print("📡 抓取 RSS...")
        articles.extend(fetch_from_rss(rss_feeds, max_items=5))

    # 2. 笔记源
    notes_dir = os.getenv("NOTES_DIR", "")
    if notes_dir:
        print("📝 读取笔记...")
        articles.extend(fetch_from_notes(notes_dir))

    # 3. 手动输入源（通过环境变量）
    manual_title = os.getenv("MANUAL_TITLE", "")
    manual_content = os.getenv("MANUAL_CONTENT", "")
    if manual_title and manual_content:
        print("✍️  处理手动输入...")
        from sources.manual_source import fetch_from_manual
        articles.extend(fetch_from_manual(manual_title, manual_content))

    if not articles:
        print("⚠️  没有找到任何输入源，请配置 RSS_FEEDS 或 NOTES_DIR")
        return

    print(f"\n📊 共收集 {len(articles)} 篇文章\n")

    # 遍历处理每篇文章
    for idx, article in enumerate(articles, 1):
        try:
            source_label = {
                "rss": "RSS",
                "note": "笔记",
                "manual": "手动"
            }.get(article.get("source_type", "rss"), "未知")

            print(f"[{idx}/{len(articles)}] [{source_label}] {article['title'][:50]}...")

            # 执行状态机
            result = process_single_article(article)

            # 简洁日志
            if result.get("notion_url"):
                print(f"  ✅ SUCCESS")
            elif result.get("error"):
                print(f"  ❌ ERROR: {result['error']}")
            else:
                print(f"  ⏭️  SKIP: {result.get('reason', 'N/A')[:50]}")

        except KeyboardInterrupt:
            print("\n[ABORT] 用户中断")
            break
        except Exception as e:
            print(f"  ❌ FAIL: {str(e)}")
            continue

    print("\n✅ 完成")


if __name__ == "__main__":
    main()
