"""AI 预处理网关 - Iridite 极客过滤准则"""
import os
import json
from typing import Optional
from pydantic import BaseModel
from matrix.utils.client import get_anthropic_client
from matrix.utils.logger import setup_logger

logger = setup_logger(__name__)


class FilterResult(BaseModel):
    """过滤结果的严格数据结构"""
    pass_filter: bool
    category: str
    reason: str
    suggested_angle: Optional[str] = None  # pass=true 时必须提供


def filter_article(article: dict, api_key: Optional[str] = None) -> FilterResult:
    """
    使用 Claude 3.5 Haiku 快速判断文章是否值得改写

    Args:
        article: 包含 title, summary, link 的字典
        api_key: Anthropic API Key（可选，默认从环境变量读取）

    Returns:
        FilterResult 对象
    """
    client = get_anthropic_client(api_key)

    # 加载 prompt 模板
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "sniper_system.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    prompt = template.format(
        title=article['title'],
        summary=article['summary'][:500],
        link=article['link']
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        # 提取 JSON 并解析
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

        # 尝试提取第一个完整的 JSON 对象（处理 Extra data 问题）
        # 找到第一个 { 和对应的 }
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
        return FilterResult(**result_dict)

    except json.JSONDecodeError as e:
        raw_content = response.content[0].text if 'response' in locals() else "N/A"
        logger.error(
            f"JSON 解析失败 [{article['title']}]",
            extra={
                "error": str(e),
                "raw_response": raw_content[:500],  # 限制长度
                "cleaned_response": content[:500] if 'content' in locals() else "N/A",
                "article_link": article['link']
            }
        )
        return FilterResult(
            pass_filter=False,
            category="错误",
            reason=f"JSON 解析失败: {str(e)}"
        )
    except Exception as e:
        logger.error(
            f"API 调用失败 [{article['title']}]",
            extra={
                "error_type": type(e).__name__,
                "error_message": str(e),
                "article_link": article['link']
            },
            exc_info=True
        )
        return FilterResult(
            pass_filter=False,
            category="错误",
            reason=f"API 调用失败: {type(e).__name__}: {str(e)}"
        )
