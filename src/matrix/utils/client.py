"""Anthropic 客户端初始化工具"""
import os
from anthropic import Anthropic


def get_anthropic_client(api_key: str | None = None) -> Anthropic:
    """获取 Anthropic 客户端实例

    支持自定义 base_url，用于第三方 API 中转服务

    Args:
        api_key: API Key，如果为 None 则从环境变量读取

    Returns:
        Anthropic 客户端实例

    Example:
        >>> client = get_anthropic_client()
        >>> # 使用第三方 API
        >>> os.environ["ANTHROPIC_BASE_URL"] = "https://api.example.com/v1"
        >>> client = get_anthropic_client()
    """
    api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL")

    if base_url:
        # 使用自定义 base_url (第三方 API)
        return Anthropic(api_key=api_key, base_url=base_url)
    else:
        # 使用官方 API
        return Anthropic(api_key=api_key)
