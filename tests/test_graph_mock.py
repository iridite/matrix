import sys
sys.path.insert(0, 'src')

"""测试 LangGraph 状态机 - 完全模拟版本（不调用真实 API）"""
from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END, START


class ArticleState(TypedDict):
    """文章处理状态"""
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

    # Notion 处理结果
    notion_url: Optional[str]
    error: Optional[str]


class MockWorkflow:
    """模拟工作流 - 用于测试"""

    def sniper_node(self, state: ArticleState) -> ArticleState:
        """模拟过滤节点"""
        print(f"🎯 [Sniper] 过滤文章: {state['title'][:50]}...")

        # 模拟 AI 判断
        if "AI" in state["title"] or "技术" in state["title"]:
            print("  ✅ 通过过滤 [技术]: 从产品化角度分析")
            return {
                **state,
                "pass_filter": True,
                "category": "技术",
                "reason": "内容质量高",
                "suggested_angle": "从产品化角度分析 AI 技术的商业价值"
            }
        else:
            print("  ❌ 未通过过滤: 内容不符合要求")
            return {
                **state,
                "pass_filter": False,
                "category": "无关",
                "reason": "内容不符合要求",
                "suggested_angle": None
            }

    def writer_node(self, state: ArticleState) -> ArticleState:
        """模拟写作节点"""
        print(f"✍️  [Writer] 生成内容: {state['title'][:50]}...")

        # 模拟生成内容
        draft_title = f"深度解析：{state['title']}"
        draft_content = f"""# {draft_title}

## 背景

{state['summary']}

## 分析

基于 {state['suggested_angle']}，我们可以看到：

1. **市场机会**：技术创新带来新的商业模式
2. **挑战**：如何将技术转化为产品
3. **未来趋势**：AI 技术将深入各行各业

## 结论

这是一个值得关注的技术方向。

---

原文链接：{state['link']}
"""

        print(f"  ✅ 生成完成: {draft_title}")

        return {
            **state,
            "draft_title": draft_title,
            "draft_content": draft_content,
            "seo_tags": ["AI", "技术", "产品化"]
        }

    def notion_node(self, state: ArticleState) -> ArticleState:
        """模拟存储节点"""
        print(f"💾 [Notion] 保存文章: {state['draft_title'][:50]}...")

        # 模拟保存成功
        print("  ✅ 保存成功")

        return {
            **state,
            "notion_url": "https://notion.so/mock-page-id"
        }

    def should_write(self, state: ArticleState) -> Literal["writer", "end"]:
        """决策函数 - 是否进入写作节点"""
        if state.get("pass_filter"):
            return "writer"
        else:
            return "end"

    def should_save(self, state: ArticleState) -> Literal["notion", "end"]:
        """决策函数 - 是否保存到 Notion"""
        if state.get("error"):
            return "end"
        elif state.get("draft_content"):
            return "notion"
        else:
            return "end"

    def build_graph(self) -> StateGraph:
        """构建工作流图"""
        workflow = StateGraph(ArticleState)

        # 添加节点
        workflow.add_node("sniper", self.sniper_node)
        workflow.add_node("writer", self.writer_node)
        workflow.add_node("notion", self.notion_node)

        # 添加边
        workflow.add_edge(START, "sniper")

        # 条件边
        workflow.add_conditional_edges(
            "sniper",
            self.should_write,
            {
                "writer": "writer",
                "end": END
            }
        )

        workflow.add_conditional_edges(
            "writer",
            self.should_save,
            {
                "notion": "notion",
                "end": END
            }
        )

        workflow.add_edge("notion", END)

        return workflow.compile()


def test_scenario_1():
    """场景 1: 文章通过过滤并成功生成"""
    print("\n📝 场景 1: 文章通过过滤并成功生成")
    print("-" * 60)

    workflow_builder = MockWorkflow()
    graph = workflow_builder.build_graph()

    initial_state: ArticleState = {
        "title": "AI 技术的最新突破",
        "link": "https://example.com/ai-breakthrough",
        "summary": "人工智能领域取得重大进展，新算法提升了模型性能...",
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

    print(f"\n初始状态:")
    print(f"  标题: {initial_state['title']}")
    print(f"  链接: {initial_state['link']}")

    print(f"\n🔄 执行工作流...\n")
    result = graph.invoke(initial_state)

    print(f"\n✅ 工作流完成\n")
    print(f"最终状态:")
    print(f"  通过过滤: {result.get('pass_filter')}")
    print(f"  分类: {result.get('category')}")
    print(f"  建议角度: {result.get('suggested_angle')}")
    print(f"  生成标题: {result.get('draft_title')}")
    print(f"  内容长度: {len(result.get('draft_content', ''))} 字符")
    print(f"  SEO 标签: {result.get('seo_tags')}")
    print(f"  Notion URL: {result.get('notion_url')}")


def test_scenario_2():
    """场景 2: 文章未通过过滤"""
    print("\n📝 场景 2: 文章未通过过滤")
    print("-" * 60)

    workflow_builder = MockWorkflow()
    graph = workflow_builder.build_graph()

    initial_state: ArticleState = {
        "title": "今天天气真好",
        "link": "https://example.com/weather",
        "summary": "阳光明媚，适合出游...",
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

    print(f"\n初始状态:")
    print(f"  标题: {initial_state['title']}")

    print(f"\n🔄 执行工作流...\n")
    result = graph.invoke(initial_state)

    print(f"\n✅ 工作流完成\n")
    print(f"最终状态:")
    print(f"  通过过滤: {result.get('pass_filter')}")
    print(f"  原因: {result.get('reason')}")
    print(f"  生成标题: {result.get('draft_title')} (应该为 None)")
    print(f"  Notion URL: {result.get('notion_url')} (应该为 None)")


def test_workflow():
    """测试完整工作流"""
    print("🧪 测试 LangGraph 状态机工作流（模拟版本）")
    print("=" * 60)

    test_scenario_1()

    print("\n" + "=" * 60)

    test_scenario_2()

    print("\n" + "=" * 60)
    print("\n✅ 所有测试场景完成")
    print("\n工作流路径:")
    print("  场景 1: START → sniper → writer → notion → END")
    print("  场景 2: START → sniper → END")


if __name__ == "__main__":
    test_workflow()
