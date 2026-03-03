import sys
sys.path.insert(0, 'src')

"""测试 LangGraph Agent 系统"""
from agents_langgraph import collaborative_generate_langgraph

# 测试数据
test_article = {
    "title": "AI Agents Are Becoming More Autonomous",
    "summary": "Recent developments in AI agent systems show increasing autonomy and collaboration capabilities...",
    "link": "https://example.com/ai-agents",
    "suggested_angle": "探讨 AI Agent 自主协作的实际应用价值"
}

print("🚀 启动 LangGraph Agent 系统测试...\n")

try:
    result = collaborative_generate_langgraph(test_article)

    print("\n" + "="*60)
    print("📝 最终生成结果：\n")
    print(f"标题: {result.get('title', 'N/A')}")
    print(f"\n正文预览:\n{result.get('content', 'N/A')[:500]}...")
    print(f"\nSEO 标签: {', '.join(result.get('seo_tags', []))}")
    print("="*60)

    print("\n✅ LangGraph 测试成功！")

except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
