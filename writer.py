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

    prompt = f"""你是 Iridite 的内容创作者。基于以下素材，生成一篇降维打击式的深度文章。

# 原始素材
标题：{article['title']}
摘要：{article['summary']}
链接：{article['link']}

# 切入点
{suggested_angle}

# 写作要求
- 标题：吸引极客的标题（不超过 50 字）
- 正文：1500-2000 字，包含技术分析、开发者视角、实战价值
- 风格：直接、犀利、有态度，避免空话套话
- SEO 标签：3-5 个关键词

# 输出格式（严格 JSON）
{{
  "title": "最终标题",
  "content": "完整正文（Markdown 格式）",
  "seo_tags": ["标签1", "标签2", "标签3"],
  "original_url": "{article['link']}"
}}"""

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text
        import json
        result_dict = json.loads(content)
        return ArticleOutput(**result_dict)

    except Exception as e:
        print(f"❌ 生成失败 [{article['title']}]: {e}")
        raise
