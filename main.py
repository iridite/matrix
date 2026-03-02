"""Matrix 主流水线 - 绝对线性控制流"""
import os
from dotenv import load_dotenv
from fetcher import fetch_feeds
from sniper import filter_article
from writer import generate_article
from notion_sink import save_to_notion
from config import AGENT_MODE

# 条件导入 Agent 模块
if AGENT_MODE == "basic":
    from agents import collaborative_generate
elif AGENT_MODE == "langgraph":
    from agents_langgraph import collaborative_generate_langgraph
elif AGENT_MODE == "langgraph_enhanced":
    from agents_langgraph_enhanced import collaborative_generate_enhanced

load_dotenv()

RSS_FEEDS = ["https://hnrss.org/frontpage", "https://www.reddit.com/r/programming/.rss"]
MAX_ITEMS = 5
NOTION_DB_ID = os.getenv("NOTION_DATABASE_ID")


def main():
    """主管道：RSS -> 过滤 -> 改写 -> 存储"""
    # 显示当前模式
    if AGENT_MODE == "basic":
        mode = "Multi-Agent (基础)"
    elif AGENT_MODE == "langgraph":
        mode = "Multi-Agent (LangGraph)"
    elif AGENT_MODE == "langgraph_enhanced":
        mode = "Multi-Agent (LangGraph + Notion 工具)"
    else:
        mode = "单 AI"

    print(f"🚀 Matrix 流水线启动 [{mode} 模式]\n")

    print("📡 [1/4] 抓取 RSS...")
    articles = fetch_feeds(RSS_FEEDS, max_items_per_feed=MAX_ITEMS)

    for idx, article in enumerate(articles, 1):
        print(f"\n--- 处理 {idx}/{len(articles)}: {article['title'][:50]}...")

        try:
            print("🎯 [2/4] AI 过滤...")
            result = filter_article(article)

            if not result.pass_filter:
                print(f"❌ 未通过: {result.reason}")
                continue

            print(f"✅ 通过 [{result.category}]: {result.suggested_angle}")

            print("✍️  [3/4] AI 生成...")

            # 根据配置选择生成模式
            if AGENT_MODE == "basic":
                # 基础 Multi-Agent 模式
                article_data = {
                    **article,
                    "suggested_angle": result.suggested_angle
                }
                output_dict = collaborative_generate(article_data)
            elif AGENT_MODE == "langgraph":
                # LangGraph Agent 模式
                article_data = {
                    **article,
                    "suggested_angle": result.suggested_angle
                }
                output_dict = collaborative_generate_langgraph(article_data)
            elif AGENT_MODE == "langgraph_enhanced":
                # 增强版 LangGraph Agent 模式（集成 Notion 工具）
                article_data = {
                    **article,
                    "suggested_angle": result.suggested_angle
                }
                output_dict = collaborative_generate_enhanced(article_data)
            else:
                # 单 AI 模式
                output = generate_article(article, result.suggested_angle)
                output_dict = output.model_dump()

            print("💾 [4/4] 写入 Notion...")
            save_to_notion(output_dict, NOTION_DB_ID)

        except KeyboardInterrupt:
            print("\n⚠️  用户中断，立即退出")
            break
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            continue

    print("\n✅ 流水线完成")


if __name__ == "__main__":
    main()
