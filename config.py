# Matrix 配置文件

# 是否启用 Multi-Agent 协作模式
# True: 使用多个 AI Agent 协作生成内容（成本更高，质量更好）
# False: 使用单个 AI 生成内容（成本更低，速度更快）
ENABLE_MULTI_AGENT = False

# Multi-Agent 模式下的 Writer Agent 风格列表
AGENT_PERSONAS = [
    "极简风格",
    "深度分析",
    "实用主义"
]

# RSS 抓取配置
MAX_ITEMS_PER_FEED = 10

# API 超时设置（秒）
API_TIMEOUT = 30
