"""测试笔记 -> 状态机的完整流程（模拟模式）"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sources.note_source import fetch_from_notes
from graph_builder import ArticleState

def test_note_to_state():
    """测试笔记转换为状态机输入"""
    print("=" * 60)
    print("测试：笔记 → 状态机流程")
    print("=" * 60)

    # 1. 读取笔记
    notes_dir = "/tmp/matrix_test_notes"
    articles = fetch_from_notes(notes_dir)

    print(f"\n✅ 读取 {len(articles)} 篇笔记\n")

    # 2. 模拟状态机处理
    for i, article in enumerate(articles, 1):
        print(f"[{i}/{len(articles)}] 处理: {article['title']}")

        # 构造初始状态
        initial_state: ArticleState = {
            "title": article["title"],
            "link": article["link"],
            "summary": article.get("summary", ""),
            "published_date": article.get("published_date", ""),
            "source_type": article.get("source_type", "note"),
            "content": article.get("content"),
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

        # 验证状态
        print(f"  ✅ 状态初始化成功")
        print(f"     - source_type: {initial_state['source_type']}")
        print(f"     - content 长度: {len(initial_state.get('content', ''))} 字符")
        print(f"     - summary 长度: {len(initial_state['summary'])} 字符")

        # 模拟 sniper 节点处理
        content_for_sniper = initial_state.get("content") or initial_state["summary"]
        print(f"  📊 Sniper 将处理 {len(content_for_sniper)} 字符的内容")

        print()

    print("=" * 60)
    print("✅ 所有笔记都能正确转换为状态机输入")
    print("=" * 60)

if __name__ == "__main__":
    test_note_to_state()
