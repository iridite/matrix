"""AI 核心加工厂 - 长文脚本生成"""
import os
from typing import Optional
from pydantic import BaseModel
from anthropic import Anthropic


class ArticleOutput(BaseModel):
    """生成文章的严格数据结构"""
    title: str
    content: str
    seo_tags: list[str]
    original_url: str


def generate_article(
    article: dict,
    suggested_angle: str,
    api_key: Optional[str] = None
) -> ArticleOutput:
    """
    使用 Claude 3.5 Sonnet 生成深度改写文章

    Args:
        article: 原始文章字典
        suggested_angle: 从 sniper 传来的切入点
        api_key: Anthropic API Key

    Returns:
        ArticleOutput 对象
    """
    client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

    # 加载 prompt 模板
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "writer_system.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    prompt = template.format(
        suggested_angle=suggested_angle,
        article_summary=f"标题：{article['title']}\n摘要：{article['summary']}\n链接：{article['link']}"
    )

    prompt += """

【输出格式（严格 JSON）】
{{
  "title": "最终标题",
  "content": "完整正文（Markdown 格式）",
  "seo_tags": ["标签1", "标签2", "标签3"],
  "original_url": "{original_url}"
}}""".format(original_url=article['link'])

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text
        import json
        import re

        # 尝试提取 Markdown 代码块中的 JSON
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)

        result_dict = json.loads(content)
        return ArticleOutput(**result_dict)

    except Exception as e:
        print(f"❌ 生成失败 [{article['title']}]: {e}")
        raise
