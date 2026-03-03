"""Matrix 主流水线 - 绝对线性控制流"""
import os
from dotenv import load_dotenv
from matrix.core.fetcher import fetch_feeds
from matrix.core.sniper import filter_article
from matrix.core.writer import generate_article
from matrix.sinks.notion_sink import save_to_notion
from matrix.config import AGENT_MODE
from matrix.utils.logger import setup_logger

logger = setup_logger(__name__)

# 条件导入 Agent 模块
if AGENT_MODE == "basic":
    from matrix.agents.agents import collaborative_generate
elif AGENT_MODE == "langgraph":
    from matrix.agents.agents_langgraph import collaborative_generate_langgraph
elif AGENT_MODE == "langgraph_enhanced":
    from matrix.agents.agents_langgraph_enhanced import collaborative_generate_enhanced

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

    logger.info(f"Matrix 流水线启动 [{mode} 模式]")

    logger.info("开始抓取 RSS 源")
    articles = fetch_feeds(RSS_FEEDS, max_items_per_feed=MAX_ITEMS)
    logger.info(f"成功抓取 {len(articles)} 篇文章")

    for idx, article in enumerate(articles, 1):
        logger.info(f"处理文章 {idx}/{len(articles)}: {article['title'][:50]}")

        try:
            logger.info("执行 AI 过滤")
            result = filter_article(article)

            if not result.pass_filter:
                logger.info(f"文章未通过过滤: {result.reason}")
                continue

            logger.info(f"文章通过过滤 [{result.category}]: {result.suggested_angle}")

            logger.info("开始 AI 生成内容")

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

            logger.info("开始写入 Notion")
            save_to_notion(output_dict, NOTION_DB_ID)
            logger.info("文章处理完成")

        except KeyboardInterrupt:
            logger.warning("用户中断，立即退出")
            break
        except Exception as e:
            logger.error(
                f"文章处理失败: {article['title'][:50]}",
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "article_link": article.get('link', 'N/A')
                },
                exc_info=True
            )
            continue

    logger.info("流水线执行完成")


if __name__ == "__main__":
    main()
