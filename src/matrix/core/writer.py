"""AI 核心加工厂 - 长文脚本生成"""
import os
import json
from typing import Optional
from pydantic import BaseModel
from matrix.utils.client import get_anthropic_client
from matrix.utils.logger import setup_logger

logger = setup_logger(__name__)


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
    client = get_anthropic_client(api_key)

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

        # 清理可能的 markdown 代码块包裹
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # 提取第一个完整的 JSON 对象
        start_idx = content.find('{')
        if start_idx != -1:
            brace_count = 0
            for i in range(start_idx, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        content = content[start_idx:i+1]
                        break

        result_dict = json.loads(content)
        return ArticleOutput(**result_dict)

    except json.JSONDecodeError as e:
        raw_content = response.content[0].text if 'response' in locals() else "N/A"
        logger.error(
            f"JSON 解析失败 [{article['title']}]",
            extra={
                "error": str(e),
                "raw_response": raw_content[:500],
                "cleaned_response": content[:500] if 'content' in locals() else "N/A",
                "article_link": article['link']
            }
        )
        raise
    except Exception as e:
        logger.error(
            f"文章生成失败 [{article['title']}]",
            extra={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "article_link": article['link']
            },
            exc_info=True
        )
        raise
