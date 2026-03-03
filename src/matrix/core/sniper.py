"""AI 预处理网关 - Iridite 极客过滤准则"""
import os
from typing import Optional
from pydantic import BaseModel
from anthropic import Anthropic


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
    client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

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
        import json
        result_dict = json.loads(content)
        return FilterResult(**result_dict)

    except Exception as e:
        print(f"⚠️  过滤失败 [{article['title']}]: {e}")
        # 默认拒绝
        return FilterResult(
            pass_filter=False,
            category="错误",
            reason=f"API 调用失败: {str(e)}"
        )
