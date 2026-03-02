"""测试 LangGraph 状态机 - 使用模拟数据"""
from graph_builder import MatrixWorkflow, ArticleState

def test_workflow():
    """测试完整工作流"""
    print("🧪 测试 LangGraph 状态机工作流\n")
    print("=" * 60)

    # 创建工作流
    workflow_builder = MatrixWorkflow(notion_db_id="test-db-id")
    graph = workflow_builder.build_graph()

    # 测试场景 1: 正常流程
    print("\n📝 场景 1: 文章通过过滤并成功生成")
    print("-" * 60)

    initial_state: ArticleState = {
        "title": "AI 技术的最新突破",
        "link": "https://example.com/ai-breakthrough",
        "summary": "人工智能领域取得重大进展...",
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

    print(f"初始状态:")
    print(f"  标题: {initial_state['title']}")
    print(f"  链接: {initial_state['link']}")
    print(f"  摘要: {initial_state['summary'][:50]}...")

    try:
        print("\n🔄 执行工作流...")
        result = graph.invoke(initial_state)

        print("\n✅ 工作流完成")
        print(f"\n最终状态:")
        print(f"  通过过滤: {result.get('pass_filter')}")
        print(f"  分类: {result.get('category')}")
        print(f"  建议角度: {result.get('suggested_angle')}")
        print(f"  生成标题: {result.get('draft_title')}")
        print(f"  内容长度: {len(result.get('draft_content', '')) if result.get('draft_content') else 0} 字符")
        print(f"  SEO 标签: {result.get('seo_tags')}")
        print(f"  Notion URL: {result.get('notion_url')}")
        print(f"  错误: {result.get('error')}")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)

    # 测试场景 2: 模拟过滤失败
    print("\n📝 场景 2: 文章未通过过滤")
    print("-" * 60)

    # 手动模拟过滤失败的状态
    failed_state: ArticleState = {
        "title": "无关内容",
        "link": "https://example.com/irrelevant",
        "summary": "这是一篇无关的文章...",
        "published_date": "2026-03-03",
        "pass_filter": False,
        "category": "无关",
        "reason": "内容不符合要求",
        "suggested_angle": None,
        "draft_title": None,
        "draft_content": None,
        "seo_tags": None,
        "notion_url": None,
        "error": None
    }

    print(f"模拟状态:")
    print(f"  标题: {failed_state['title']}")
    print(f"  通过过滤: {failed_state['pass_filter']}")
    print(f"  原因: {failed_state['reason']}")

    print("\n预期结果: 工作流应该在 sniper 节点后直接结束")

    print("\n" + "=" * 60)
    print("\n✅ 所有测试场景完成")


if __name__ == "__main__":
    test_workflow()
