# Matrix 配置文件

# Agent 模式选择
# False: 单 AI 模式（writer.py，最快最便宜）
# "basic": 基础 Multi-Agent（agents.py，固定流程：3个Writer → Critic → Editor）
# "langgraph": LangGraph Agent（agents_langgraph.py，自主迭代：Research → Writer ⇄ Critic → Editor）
# "langgraph_enhanced": 增强版 LangGraph（agents_langgraph_enhanced.py，集成 Notion 工具）
AGENT_MODE = False  # False | "basic" | "langgraph" | "langgraph_enhanced"

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
