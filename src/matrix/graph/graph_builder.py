"""LangGraph 状态机工作流 - 严格架构版本"""
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END
from matrix.core.fetcher import fetch_feeds
from matrix.core.sniper import filter_article
from matrix.core.writer import generate_article
from matrix.sinks.notion_sink import save_to_notion


class ArticleState(TypedDict):
    """文章处理状态 - 全局状态定义"""
    # 原始数据
    title: str
    link: str
    summary: str
    published_date: str

    # Sniper 处理结果
    pass_filter: bool
    category: Optional[str]
    reason: Optional[str]
    suggested_angle: Optional[str]

    # Writer 处理结果
    draft_title: Optional[str]
    draft_content: Optional[str]
    seo_tags: Optional[list[str]]

    # 图片渲染
    local_media_list: Optional[list[str]]  # 本地图片路径列表
    final_card_path: Optional[str]  # 生成的卡片路径

    # Notion 处理结果
    notion_url: Optional[str]
    error: Optional[str]


# ============================================================
# 节点函数 (Nodes) - 包装现有模块
# ============================================================

def node_sniper(state: ArticleState) -> dict:
    """
    Sniper 节点 - 调用 sniper.py 的过滤逻辑

    返回要更新的状态字段
    """
    try:
        # 构造 sniper 需要的输入格式
        article = {
            "title": state["title"],
            "link": state["link"],
            "summary": state["summary"]
        }

        # 调用 sniper 模块
        result = filter_article(article)

        # 返回要更新的状态
        return {
            "pass_filter": result.pass_filter,
            "category": result.category,
            "reason": result.reason,
            "suggested_angle": result.suggested_angle
        }

    except Exception as e:
        return {
            "pass_filter": False,
            "category": "错误",
            "reason": f"Sniper 失败: {str(e)}",
            "error": str(e)
        }


def node_writer(state: ArticleState) -> dict:
    """
    Writer 节点 - 调用 writer.py 的生成逻辑

    返回要更新的状态字段
    """
    try:
        # 构造 writer 需要的输入格式
        article = {
            "title": state["title"],
            "link": state["link"],
            "summary": state["summary"]
        }

        # 调用 writer 模块
        output = generate_article(article, state["suggested_angle"] or "")

        # 返回要更新的状态
        return {
            "draft_title": output.title,
            "draft_content": output.content,
            "seo_tags": output.seo_tags
        }

    except Exception as e:
        return {
            "error": f"Writer 失败: {str(e)}"
        }


def node_notion(state: ArticleState) -> dict:
    """
    Notion 节点 - 调用 notion_sink.py 的存储逻辑

    返回要更新的状态字段
    """
    try:
        # 构造 notion_sink 需要的输入格式
        article_output = {
            "title": state["draft_title"],
            "content": state["draft_content"],
            "seo_tags": state["seo_tags"],
            "original_url": state["link"]
        }

        # 从环境变量获取 Database ID
        import os
        db_id = os.getenv("NOTION_DATABASE_ID")

        # 调用 notion_sink 模块
        success = save_to_notion(article_output, db_id)

        # 返回要更新的状态
        if success:
            return {"notion_url": "已保存"}
        else:
            return {"error": "Notion 保存失败"}

    except Exception as e:
        return {
            "error": f"Notion 失败: {str(e)}"
        }


# ============================================================
# 路由函数 (Conditional Edge)
# ============================================================

def should_write(state: ArticleState) -> Literal["writer", "END"]:
    """
    核心路由函数 - 决定是否进入 Writer 节点

    Returns:
        "writer" - 通过过滤，进入写作
        "END" - 未通过过滤，直接结束
    """
    if state.get("pass_filter"):
        return "writer"
    else:
        return "END"


# ============================================================
# 组装 StateGraph
# ============================================================

def build_graph() -> StateGraph:
    """
    构建完整的 LangGraph 状态机

    流程:
        START -> sniper -> [条件判断]
                          ├─ 通过 -> writer -> notion -> END
                          └─ 拒绝 -> END
    """
    # 实例化 StateGraph
    workflow = StateGraph(ArticleState)

    # 添加节点
    workflow.add_node("sniper", node_sniper)
    workflow.add_node("writer", node_writer)
    workflow.add_node("notion", node_notion)

    # 设置入口点
    workflow.set_entry_point("sniper")

    # 添加条件边：从 sniper 出发，使用 should_write 路由
    workflow.add_conditional_edges(
        "sniper",
        should_write,
        {
            "writer": "writer",
            "END": END
        }
    )

    # 添加普通边：writer -> notion -> END
    workflow.add_edge("writer", "notion")
    workflow.add_edge("notion", END)

    # 编译
    return workflow.compile()


# ============================================================
# 导出接口
# ============================================================

def process_single_article(article: dict) -> ArticleState:
    """
    处理单篇文章

    Args:
        article: 来自 fetcher 的文章数据

    Returns:
        最终状态
    """
    # 构建图
    app = build_graph()

    # 初始化状态
    initial_state: ArticleState = {
        "title": article["title"],
        "link": article["link"],
        "summary": article.get("summary", ""),
        "published_date": article.get("published_date", ""),
        "pass_filter": False,
        "category": None,
        "reason": None,
        "suggested_angle": None,
        "draft_title": None,
        "draft_content": None,
        "seo_tags": None,
        "local_media_list": None,
        "final_card_path": None,
        "notion_url": None,
        "error": None
    }

    # 执行工作流
    result = app.invoke(initial_state)

    return result
