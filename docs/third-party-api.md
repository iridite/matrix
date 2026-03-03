# 第三方 Anthropic API 支持

Matrix 支持使用第三方 Anthropic API 中转服务,方便国内用户或需要使用代理的场景。

## 配置方法

### 1. 环境变量配置

在 `.env` 文件中添加:

```env
# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 第三方 API Base URL (可选)
# 留空则使用官方 API: https://api.anthropic.com
ANTHROPIC_BASE_URL=https://api.example.com/v1
```

### 2. 支持的第三方服务

常见的第三方 API 服务:

- **OpenRouter**: `https://openrouter.ai/api/v1`
- **自建中转**: 根据你的中转服务地址配置

## 使用示例

### 基本使用

```python
from matrix.utils.client import get_anthropic_client

# 使用环境变量配置
client = get_anthropic_client()

# 或直接传递 API Key
client = get_anthropic_client(api_key="your-key")
```

### 完整流程

```python
import os
from matrix.core.fetcher import fetch_feeds
from matrix.core.sniper import filter_article
from matrix.core.writer import generate_article

# 配置第三方 API
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-xxx"
os.environ["ANTHROPIC_BASE_URL"] = "https://api.example.com/v1"

# 正常使用 Matrix
articles = fetch_feeds(["https://hnrss.org/frontpage"])
for article in articles:
    result = filter_article(article)
    if result.pass_filter:
        output = generate_article(article, result.suggested_angle)
        print(output.title)
```

## 注意事项

1. **API 兼容性**: 确保第三方服务完全兼容 Anthropic API
2. **模型支持**: 确认第三方服务支持 `claude-sonnet-4-5-20250929` 模型
3. **速率限制**: 不同服务的速率限制可能不同
4. **安全性**: 使用可信的第三方服务,保护好你的 API Key

## 测试

运行测试验证配置:

```bash
uv run python tests/test_third_party_api.py
```

## 故障排查

### 连接失败

```python
# 检查 base_url 是否正确
import os
from matrix.utils.client import get_anthropic_client

os.environ["ANTHROPIC_BASE_URL"] = "https://api.example.com/v1"
client = get_anthropic_client()
print(f"Base URL: {client.base_url}")
```

### API 响应错误

- 确认第三方服务是否正常运行
- 检查 API Key 是否有效
- 查看第三方服务的日志
