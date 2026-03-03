"""测试第三方 Anthropic API 支持"""
import os
import pytest
from matrix.utils.client import get_anthropic_client


def test_get_client_default():
    """测试默认客户端初始化"""
    # 设置测试 API Key
    os.environ["ANTHROPIC_API_KEY"] = "test-key"

    client = get_anthropic_client()
    assert client is not None
    assert client.api_key == "test-key"


def test_get_client_with_custom_base_url():
    """测试自定义 base_url"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    os.environ["ANTHROPIC_BASE_URL"] = "https://api.example.com/v1"

    client = get_anthropic_client()
    assert client is not None
    # Anthropic 客户端会自动在 base_url 末尾添加 /
    assert str(client.base_url) == "https://api.example.com/v1/"

    # 清理环境变量
    del os.environ["ANTHROPIC_BASE_URL"]


def test_get_client_with_api_key_param():
    """测试通过参数传递 API Key"""
    client = get_anthropic_client(api_key="custom-key")
    assert client is not None
    assert client.api_key == "custom-key"


if __name__ == "__main__":
    print("🧪 测试第三方 API 支持...")

    # 测试 1: 默认客户端
    print("\n1️⃣ 测试默认客户端初始化...")
    test_get_client_default()
    print("✅ 通过")

    # 测试 2: 自定义 base_url
    print("\n2️⃣ 测试自定义 base_url...")
    test_get_client_with_custom_base_url()
    print("✅ 通过")

    # 测试 3: 参数传递 API Key
    print("\n3️⃣ 测试参数传递 API Key...")
    test_get_client_with_api_key_param()
    print("✅ 通过")

    print("\n✅ 所有测试通过!")
