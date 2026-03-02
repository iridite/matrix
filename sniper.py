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

    prompt = f"""你是 Iridite 极客媒体的内容筛选器。判断以下新闻是否值得深度改写。

# 过滤准则
✅ 通过：技术突破、开源项目、开发者工具、AI/编程/基础设施创新
❌ 拒绝：营销软文、融资新闻、人事变动、纯商业报道

# 待评估文章
标题：{article['title']}
摘要：{article['summary'][:500]}
链接：{article['link']}

# 输出要求（严格 JSON）
{{
  "pass_filter": true/false,
  "category": "技术/工具/AI/开源/其他",
  "reason": "一句话说明理由",
  "suggested_angle": "如果通过，提供降维打击的切入点（如：从开发者痛点切入、对比竞品、技术原理拆解）"
}}"""

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
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
