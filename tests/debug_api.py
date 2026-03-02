"""调试 API 响应格式"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def debug_api_response():
    """查看 API 实际返回的内容"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    # 简单测试
    test_article = {
        "title": "Python uv 踩坑记录",
        "summary": "今天在用 uv 管理项目依赖时遇到了一些问题，记录一下解决方案。",
        "link": "file:///tmp/test.md"
    }

    # 加载 prompt
    prompt_path = Path(__file__).parent.parent / "prompts" / "sniper_system.txt"
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    prompt = template.format(
        title=test_article['title'],
        summary=test_article['summary'],
        link=test_article['link']
    )

    print("=" * 60)
    print("发送的 Prompt:")
    print("=" * 60)
    print(prompt[:500])
    print("\n...")

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        print("\n" + "=" * 60)
        print("API 响应:")
        print("=" * 60)
        print(f"类型: {type(response.content[0])}")
        print(f"文本内容:\n{response.content[0].text}")
        print("=" * 60)

        # 尝试解析
        import json
        try:
            result = json.loads(response.content[0].text)
            print("\n✅ JSON 解析成功:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"\n❌ JSON 解析失败: {e}")
            print(f"   原始内容: {repr(response.content[0].text[:200])}")

    except Exception as e:
        print(f"\n❌ API 调用失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_response()
