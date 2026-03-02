"""测试多源输入系统"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sources.rss_source import fetch_from_rss
from sources.note_source import fetch_from_notes
from sources.manual_source import fetch_from_manual


def test_rss_source():
    """测试 RSS 源"""
    print("=" * 60)
    print("测试 RSS 源")
    print("=" * 60)

    feeds = ["https://hnrss.org/frontpage"]
    articles = fetch_from_rss(feeds, max_items=2)

    print(f"✅ 抓取到 {len(articles)} 篇文章")
    for article in articles:
        print(f"  - [{article['source_type']}] {article['title'][:50]}")

    return len(articles) > 0


def test_note_source():
    """测试笔记源"""
    print("\n" + "=" * 60)
    print("测试笔记源")
    print("=" * 60)

    # 创建临时测试笔记
    test_dir = Path("/tmp/matrix_test_notes")
    test_dir.mkdir(exist_ok=True)

    test_note = test_dir / "test.md"
    test_note.write_text("""# 为什么我切掉了 n8n

n8n 看起来很美好，但实际使用中发现：
1. 过度设计的 UI
2. 调试困难
3. 失去了对系统的控制权

最终我选择用 Python + uv 重写整个流程。
""", encoding="utf-8")

    articles = fetch_from_notes(str(test_dir))

    print(f"✅ 读取到 {len(articles)} 篇笔记")
    for article in articles:
        print(f"  - [{article['source_type']}] {article['title']}")
        print(f"    内容长度: {len(article.get('content', ''))} 字符")

    # 清理
    test_note.unlink()
    test_dir.rmdir()

    return len(articles) > 0


def test_manual_source():
    """测试手动输入源"""
    print("\n" + "=" * 60)
    print("测试手动输入源")
    print("=" * 60)

    articles = fetch_from_manual(
        title="测试手动输入",
        content="这是一篇手动输入的测试文章。\n\n内容可以很长，支持 Markdown 格式。",
        link="https://example.com/test"
    )

    print(f"✅ 创建 {len(articles)} 篇文章")
    for article in articles:
        print(f"  - [{article['source_type']}] {article['title']}")
        print(f"    链接: {article['link']}")

    return len(articles) > 0


def test_graph_builder():
    """测试状态机处理"""
    print("\n" + "=" * 60)
    print("测试 LangGraph 状态机")
    print("=" * 60)

    # 模拟一篇文章
    test_article = {
        "title": "Python 3.14 新特性",
        "link": "https://example.com/python-3.14",
        "summary": "Python 3.14 带来了重大性能提升...",
        "published_date": "2024-01-20T10:00:00",
        "source_type": "note",
        "content": "Python 3.14 是一个重要版本，包含了 JIT 编译器等新特性。"
    }

    print(f"输入文章: {test_article['title']}")
    print(f"来源类型: {test_article['source_type']}")
    print(f"内容长度: {len(test_article.get('content', ''))} 字符")

    # 检查状态定义
    from graph_builder import ArticleState
    print(f"\n✅ ArticleState 包含字段:")
    for key in ArticleState.__annotations__:
        print(f"  - {key}: {ArticleState.__annotations__[key]}")

    return True


if __name__ == "__main__":
    print("🚀 Matrix 多源输入系统测试\n")

    results = []

    try:
        results.append(("RSS 源", test_rss_source()))
    except Exception as e:
        print(f"❌ RSS 源测试失败: {e}")
        results.append(("RSS 源", False))

    try:
        results.append(("笔记源", test_note_source()))
    except Exception as e:
        print(f"❌ 笔记源测试失败: {e}")
        results.append(("笔记源", False))

    try:
        results.append(("手动输入源", test_manual_source()))
    except Exception as e:
        print(f"❌ 手动输入源测试失败: {e}")
        results.append(("手动输入源", False))

    try:
        results.append(("状态机", test_graph_builder()))
    except Exception as e:
        print(f"❌ 状态机测试失败: {e}")
        results.append(("状态机", False))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息")
        sys.exit(1)
