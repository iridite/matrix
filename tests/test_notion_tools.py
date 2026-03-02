"""测试 Notion 工具"""
import os
from dotenv import load_dotenv
from tools.notion_tools import NotionTools

load_dotenv()

def test_notion_tools():
    """测试 Notion 工具集"""
    tools = NotionTools()
    db_id = os.getenv("NOTION_DATABASE_ID")

    print("🧪 测试 Notion 工具集\n")

    # 1. 测试搜索页面
    print("1️⃣ 测试搜索页面...")
    results = tools.search_pages("AI", max_results=3)
    print(f"   找到 {len(results)} 个页面:")
    for page in results:
        print(f"   - {page['title']}")
    print()

    # 2. 测试查询 Database
    print("2️⃣ 测试查询 Database...")
    results = tools.query_database(db_id, max_results=5)
    print(f"   找到 {len(results)} 条记录:")
    for page in results:
        print(f"   - {page['properties'].get('Name', '无标题')}")
    print()

    # 3. 测试获取最近主题
    print("3️⃣ 测试获取最近主题...")
    topics = tools.get_recent_topics(db_id)
    print(f"   最近 {len(topics)} 个主题:")
    for topic in topics[:5]:
        print(f"   - {topic}")
    print()

    # 4. 测试检查重复
    print("4️⃣ 测试检查重复...")
    test_title = "测试文章标题"
    is_duplicate = tools.check_duplicate(db_id, test_title)
    print(f"   '{test_title}' 是否重复: {is_duplicate}")
    print()

    # 5. 测试获取页面内容（如果有页面）
    if results:
        print("5️⃣ 测试获取页面内容...")
        page_id = results[0]["id"]
        content = tools.get_page_content(page_id)
        print(f"   页面内容预览 (前 200 字符):")
        print(f"   {content[:200]}...")
        print()

    print("✅ 所有测试完成")


if __name__ == "__main__":
    test_notion_tools()
