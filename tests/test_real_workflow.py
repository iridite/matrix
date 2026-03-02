"""测试真实的笔记处理工作流（单篇）"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
from sources.note_source import fetch_from_notes
from graph_builder import build_graph

# 加载环境变量
load_dotenv()

def test_single_note():
    """测试处理单篇笔记的完整流程"""
    print("=" * 60)
    print("测试：真实笔记处理工作流")
    print("=" * 60)

    # 1. 读取笔记
    notes_dir = "/tmp/matrix_test_notes"
    articles = fetch_from_notes(notes_dir)

    if not articles:
        print("❌ 没有找到笔记")
        return

    # 只处理第一篇
    article = articles[0]
    print(f"\n📝 处理笔记: {article['title']}")
    print(f"   内容长度: {len(article.get('content', ''))} 字符\n")

    # 2. 构建状态机
    app = build_graph()

    # 3. 初始化状态
    initial_state = {
        "title": article["title"],
        "link": article["link"],
        "summary": article.get("summary", ""),
        "published_date": article.get("published_date", ""),
        "source_type": article.get("source_type", "note"),
        "content": article.get("content"),
    }

    # 4. 执行工作流
    print("🚀 开始执行状态机...\n")
    try:
        result = app.invoke(initial_state)

        print("\n" + "=" * 60)
        print("执行结果:")
        print("=" * 60)
        print(f"✅ 通过过滤: {result.get('pass_filter')}")
        print(f"📂 分类: {result.get('category')}")
        print(f"💡 原因: {result.get('reason')}")

        if result.get('pass_filter'):
            print(f"\n📝 生成标题: {result.get('draft_title')}")
            print(f"📄 内容长度: {len(result.get('draft_content', ''))} 字符")
            print(f"🏷️  SEO 标签: {result.get('seo_tags')}")
            print(f"🔗 Notion URL: {result.get('notion_url')}")
        else:
            print(f"\n⏭️  文章被过滤，未生成内容")

        if result.get('error'):
            print(f"\n⚠️  错误: {result.get('error')}")

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_single_note()
