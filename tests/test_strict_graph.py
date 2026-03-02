"""测试严格架构版本的 LangGraph - 使用模拟数据"""
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END


class ArticleState(TypedDict):
    """文章处理状态"""
    title: str
    link: str
    summary: str
    published_date: str
    pass_filter: bool
    category: Optional[str]
    reason: Optional[str]
    suggested_angle: Optional[str]
    draft_title: Optional[str]
    draft_content: Optional[str]
    seo_tags: Optional[list[str]]
    notion_url: Optional[str]
    error: Optional[str]


# 模拟节点
def node_sniper(state: ArticleState) -> dict:
    """模拟 Sniper 节点"""
    if "AI" in state["title"] or "技术" in state["title"]:
        return {
            "pass_filter": True,
            "category": "技术",
            "reason": "内容质量高",
            "suggested_angle": "从产品化角度分析"
        }
    else:
        return {
            "pass_filter": False,
            "category": "无关",
            "reason": "内容不符合要求"
        }


def node_writer(state: ArticleState) -> dict:
    """模拟 Writer 节点"""
    return {
        "draft_title": f"深度解析：{state['title']}",
        "draft_content": f"# 内容\n\n基于 {state['suggested_angle']}...",
        "seo_tags": ["AI", "技术"]
    }


def node_notion(state: ArticleState) -> dict:
    """模拟 Notion 节点"""
    return {"notion_url": "已保存"}


def should_write(state: ArticleState) -> Literal["writer", "END"]:
    """路由函数"""
    return "writer" if state.get("pass_filter") else "END"


def build_graph() -> StateGraph:
    """构建图"""
    workflow = StateGraph(ArticleState)
    workflow.add_node("sniper", node_sniper)
    workflow.add_node("writer", node_writer)
    workflow.add_node("notion", node_notion)
    workflow.set_entry_point("sniper")
    workflow.add_conditional_edges("sniper", should_write, {"writer": "writer", "END": END})
    workflow.add_edge("writer", "notion")
    workflow.add_edge("notion", END)
    return workflow.compile()


def test():
    """测试"""
    print("🧪 测试严格架构版本\n")

    app = build_graph()

    # 测试 1: 通过过滤
    print("测试 1: AI 文章")
    state1: ArticleState = {
        "title": "AI 技术突破",
        "link": "https://example.com",
        "summary": "...",
        "published_date": "2026-03-03",
        "pass_filter": False,
        "category": None,
        "reason": None,
        "suggested_angle": None,
        "draft_title": None,
        "draft_content": None,
        "seo_tags": None,
        "notion_url": None,
        "error": None
    }
    result1 = app.invoke(state1)
    print(f"  通过: {result1['pass_filter']}")
    print(f"  标题: {result1['draft_title']}")
    print(f"  Notion: {result1['notion_url']}\n")

    # 测试 2: 未通过过滤
    print("测试 2: 无关文章")
    state2: ArticleState = {
        "title": "天气预报",
        "link": "https://example.com",
        "summary": "...",
        "published_date": "2026-03-03",
        "pass_filter": False,
        "category": None,
        "reason": None,
        "suggested_angle": None,
        "draft_title": None,
        "draft_content": None,
        "seo_tags": None,
        "notion_url": None,
        "error": None
    }
    result2 = app.invoke(state2)
    print(f"  通过: {result2['pass_filter']}")
    print(f"  原因: {result2['reason']}")
    print(f"  标题: {result2['draft_title']} (应为 None)")
    print(f"  Notion: {result2['notion_url']} (应为 None)\n")

    print("✅ 测试完成")


if __name__ == "__main__":
    test()
