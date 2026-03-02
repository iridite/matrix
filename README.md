# Matrix - 全自动内容降维打击流水线

> 取代臃肿的 n8n，用纯 Python 实现绝对线性的内容处理管道

## 架构理念

- **极小执行力**：拒绝过度设计，函数式管道，零 Class 继承树
- **绝对容错**：单篇失败不崩溃，Ctrl+C 瞬间中断
- **高租售比**：每行代码都有明确价值

## 工作流模式

Matrix 支持四种内容生成模式，在 `config.py` 中配置：

### 模式 1: 单 AI 模式（默认）
```python
AGENT_MODE = False
```

**流程：**
```
RSS 抓取 → AI 过滤 → AI 改写 → Notion 存储
(fetcher) → (sniper) → (writer) → (notion_sink)
```

**特点：**
- 最快最便宜（1 次 API 调用生成内容）
- 适合快速批量生成
- 质量稳定但缺乏多样性

### 模式 2: 基础 Multi-Agent
```python
AGENT_MODE = "basic"
```

**流程：**
```
RSS 抓取 → AI 过滤 → Multi-Agent 协作 → Notion 存储
                        ↓
            3个 Writer (并行) → Critic → Editor
            (极简/深度/实用)
```

**特点：**
- 固定流程（5 次 API 调用）
- 多样性好，综合多个视角
- 无迭代优化

### 模式 3: LangGraph Agent（自主迭代）
```python
AGENT_MODE = "langgraph"
```

**流程：**
```
RSS 抓取 → AI 过滤 → LangGraph 自主协作 → Notion 存储
                        ↓
            Research (市场分析)
                ↓
            Writer (生成初稿)
                ↓
            Critic (评审) ←─┐
                ↓           │
            满意？          │
            ├─ 是 → Editor  │
            └─ 否 ─────────┘ (最多 3 次)
```

**特点：**
- **自主迭代**：Critic 自动判断质量，不满意则触发重写
- **动态流程**：4-8 次 API 调用（根据质量动态调整）
- **市场导向**：Research Agent 分析热点和受众需求
- **质量优先**：持续优化直到满意或达到最大迭代次数

### 模式 4: 增强版 LangGraph（集成 Notion 工具）⭐ 新功能
```python
AGENT_MODE = "langgraph_enhanced"
```

**流程：**
```
RSS 抓取 → AI 过滤 → 增强版 LangGraph → Notion 存储
                        ↓
            Research (市场分析 + Notion 查询)
                ↓
            ├─ 检查重复文章
            ├─ 获取最近主题
            └─ 搜索相关内容
                ↓
            Writer (生成初稿)
                ↓
            Critic (评审) ←─┐
                ↓           │
            满意？          │
            ├─ 是 → Editor  │
            └─ 否 ─────────┘ (最多 3 次)
```

**特点：**
- ✅ **Notion 集成**：Agent 可以查询历史文章，避免重复
- ✅ **上下文感知**：了解最近发布的主题，保持内容多样性
- ✅ **智能决策**：基于历史数据调整写作角度
- ✅ **自主迭代**：继承 LangGraph 的所有优势
- 📊 **API 调用**：5-10 次（包含 Notion 查询）

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv 创建虚拟环境并安装
uv venv
source .venv/bin/activate  # Linux/Mac
uv pip install -e .
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Keys
```

### 3. 选择工作流模式

编辑 `config.py`：
```python
# 选择一种模式
AGENT_MODE = False          # 单 AI（快速）
AGENT_MODE = "basic"        # 基础 Multi-Agent（多样性）
AGENT_MODE = "langgraph"    # LangGraph（自主迭代）
```

### 4. 运行

```bash
python main.py
```

## 核心模块说明

### `fetcher.py` - RSS 抓取器
- 输入：RSS/Atom URL 列表
- 输出：标准化文章字典
- 特性：物理截断（防 API 暴走）

### `sniper.py` - AI 预处理网关
- 模型：Claude Sonnet 4.5
- 任务：判断文章是否值得改写
- 输出：`FilterResult` (Pydantic 严格校验)

### 内容生成模块

#### `writer.py` - 单 AI 生成器
- 模型：Claude Sonnet 4.5
- 任务：一次性生成完整文章
- 输出：`ArticleOutput` (标题/正文/SEO)

#### `agents.py` - 基础 Multi-Agent
- 3 个 Writer Agent（不同风格）
- 1 个 Critic Agent（评审）
- 1 个 Editor Agent（综合编辑）
- 1 个 JsonParser Agent（格式化）

#### `agents_langgraph.py` - LangGraph Agent
- Research Agent（市场分析）
- Writer Agent（内容生成，支持重写）
- Critic Agent（质量评审，决策路由）
- Editor Agent（最终润色）
- 基于 LangGraph 的状态图管理

### `notion_sink.py` - Notion 存储器
- 协议：Notion API (httpx)
- 任务：写入 Database 页面内容

## Notion Database 结构

使用的 Database 只需要一个 **Name** 字段（Title 类型）。

内容会写入页面正文，包括：
- 标题（写入 Name 属性）
- 正文内容（Markdown 格式）
- 原文链接
- SEO 标签

## 容错机制

- 单个 RSS 源失败 → 打印日志，继续下一个
- 单篇文章解析失败 → 跳过，不影响其他
- API 调用超时 → 捕获异常，标记失败
- Ctrl+C 中断 → 立即退出，不等待
- LangGraph 模式：达到最大迭代次数强制通过

## 依赖

- `feedparser` - RSS/Atom 解析
- `httpx` - 异步/同步 HTTP 客户端
- `pydantic` - 数据结构校验
- `anthropic` - Claude API SDK
- `python-dotenv` - 环境变量管理
- `langgraph` - Agent 工作流编排（可选）

## 文档

- [架构设计](ARCHITECTURE.md) - 系统设计哲学
- [AI 框架分析](docs/ai-frameworks-analysis.md) - 为什么选择原生实现
- [LangGraph 探索](docs/langgraph-exploration.md) - 自主 Agent 系统设计

## License

MIT
