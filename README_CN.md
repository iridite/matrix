<div align="center">

# 🎯 Matrix

**全自动内容降维打击流水线 | AI-Powered Content Pipeline**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/iridite/matrix?style=social)](https://github.com/iridite/matrix/stargazers)

[English](README.md) | [简体中文](README_CN.md)

**取代臃肿的 n8n，用纯 Python 实现极简、高效、可控的 AI 内容处理管道**

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [架构设计](#-架构设计) • [文档](#-文档) • [社区](#-社区)

</div>

---

## 🌟 为什么选择 Matrix？

### 痛点

你是否遇到过这些问题：

- ❌ n8n 配置复杂，调试困难，黑盒运行
- ❌ 单 AI 生成内容质量不稳定，缺乏多样性
- ❌ 手动处理 RSS 订阅，效率低下
- ❌ 内容重复发布，缺乏历史查询能力
- ❌ 无法自定义 AI 协作流程

### 解决方案

Matrix 提供：

- ✅ **纯 Python 实现**：代码即配置，完全可控
- ✅ **4 种工作流模式**：从单 AI 到自主迭代，灵活选择
- ✅ **智能过滤**：AI 预处理，只处理高价值内容
- ✅ **Notion 集成**：自动去重，历史查询
- ✅ **图文卡片**：自动生成精美的社交媒体卡片
- ✅ **极简架构**：300+ 行核心代码，易于理解和扩展

---

## ✨ 功能特性

### 🎯 核心能力

| 功能 | 描述 | 状态 |
|------|------|------|
| 🤖 多模式 AI 协作 | 单 AI / Multi-Agent / LangGraph 自主迭代 | ✅ |
| 🔄 智能内容过滤 | AI 预处理网关，自动筛选高价值内容 | ✅ |
| ✍️ 风格化改写 | Iridite 风格（极简、疲惫感、冷酷建议） | ✅ |
| 🎨 图文卡片生成 | 极客风格 3:4 视觉卡片（1080x1440） | ✅ |
| 📊 Notion 集成 | 无缝写入，支持历史查询和去重 | ✅ |
| 🔌 多源输入 | RSS / 本地笔记 / 手动输入 | ✅ |
| 🌐 多语言支持 | 英文 / 日文 | 🚧 |
| 🖥️ Web UI | 可视化管理界面 | 📋 |

---

## 🚀 快速开始

### 5 分钟上手

```bash
# 1. 克隆仓库
git clone https://github.com/iridite/matrix.git
cd matrix

# 2. 安装依赖（使用 uv，速度提升 10-100x）
uv venv && source .venv/bin/activate
uv pip install -e .
uv run playwright install chromium

# 3. 配置 API Key
cp .env.example .env
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env

# 4. 运行
uv run python -m matrix.main
```

### 输出示例

```
🚀 Matrix 流水线启动 [单 AI 模式]

📡 [1/4] 抓取 RSS...
✓ 获取 5 篇文章

--- 处理 1/5: Building a RAG System with LangChain...
🎯 [2/4] AI 过滤...
✅ 通过 [技术]: 深入分析 RAG 系统架构
✍️  [3/4] AI 生成...
✓ 生成完成（2847 字）
💾 [4/4] 写入 Notion...
✓ 已保存: https://notion.so/xxx

✅ 流水线完成
```

---

## 🏗️ 架构设计

### 设计理念

Matrix 遵循 **极简主义** 和 **函数式编程** 原则：

```python
# 核心流水线（仅 10 行代码）
articles = fetch_feeds(RSS_FEEDS)           # 抓取
for article in articles:
    result = filter_article(article)        # 过滤
    if not result.pass_filter:
        continue
    output = generate_article(article)      # 生成
    save_to_notion(output, DB_ID)          # 存储
```

### 项目结构

```
matrix/
├── src/matrix/           # 核心包
│   ├── agents/          # Multi-Agent 协作系统
│   │   ├── agents.py                    # 基础 Multi-Agent
│   │   ├── agents_langgraph.py          # LangGraph Agent
│   │   └── agents_langgraph_enhanced.py # 增强版（Notion 工具）
│   ├── core/            # 核心模块
│   │   ├── fetcher.py   # RSS 抓取器
│   │   ├── sniper.py    # AI 过滤器
│   │   └── writer.py    # AI 生成器
│   ├── graph/           # LangGraph 状态机
│   │   ├── graph_builder.py  # 状态机构建器
│   │   └── main_graph.py     # 调度中心
│   ├── renderers/       # 图文卡片渲染器
│   │   └── image_renderer.py
│   ├── sinks/           # 输出模块
│   │   └── notion_sink.py
│   ├── tools/           # 工具集
│   │   └── notion_tools.py   # Notion API 工具
│   ├── config.py        # 配置文件
│   └── main.py          # 主入口
├── prompts/             # AI Prompt 模板
├── docs/                # 文档
├── tests/               # 测试套件
└── scripts/             # 辅助脚本
```

---

## 🔧 工作流模式对比

| 模式 | API 调用 | 质量 | 速度 | 成本 | 适用场景 |
|------|---------|------|------|------|---------|
| 单 AI | 1 次 | ⭐⭐⭐ | ⚡⚡⚡ | 💰 | 快速批量生成 |
| Multi-Agent | 5 次 | ⭐⭐⭐⭐ | ⚡⚡ | 💰💰 | 多样性内容 |
| LangGraph | 4-8 次 | ⭐⭐⭐⭐⭐ | ⚡ | 💰💰💰 | 高质量内容 |
| 增强版 | 5-10 次 | ⭐⭐⭐⭐⭐ | ⚡ | 💰💰💰 | 智能去重 + 高质量 |

### 模式选择建议

- **快速原型**：单 AI 模式
- **日常使用**：Multi-Agent 模式
- **重要内容**：LangGraph 模式
- **生产环境**：增强版（推荐）

---

## 📦 核心模块详解

### 🎣 Fetcher - RSS 抓取器

**功能：** 从 RSS/Atom 源抓取文章

**特性：**
- ✅ 支持多个 RSS 源并行抓取
- ✅ 物理截断防止 API 暴走（max_items_per_feed）
- ✅ 标准化输出格式
- ✅ 容错处理（单源失败不影响其他）

**使用：**
```python
from matrix.core.fetcher import fetch_feeds

articles = fetch_feeds(
    feeds=[
        "https://hnrss.org/frontpage",
        "https://www.reddit.com/r/programming/.rss"
    ],
    max_items_per_feed=5
)
# 返回: [{"title": "...", "link": "...", "summary": "...", ...}, ...]
```

---

### 🎯 Sniper - AI 预处理网关

**功能：** 智能过滤，只处理高价值内容

**特性：**
- ✅ Claude Sonnet 4.5 驱动
- ✅ Pydantic 严格校验（FilterResult）
- ✅ 智能分类（技术/工具/观点/教程等）
- ✅ 建议写作角度

**使用：**
```python
from matrix.core.sniper import filter_article

result = filter_article(article)
# FilterResult(
#     pass_filter=True,
#     category="技术",
#     reason="深度技术分析，适合改写",
#     suggested_angle="从架构设计角度分析..."
# )
```

---

### ✍️ Writer - 内容生成器

**功能：** AI 改写，生成 Iridite 风格内容

**特性：**
- ✅ Claude Sonnet 4.5 驱动
- ✅ Iridite 风格（极简、疲惫感、冷酷建议）
- ✅ 自动生成 SEO 标签
- ✅ Pydantic 严格校验（ArticleOutput）

**使用：**
```python
from matrix.core.writer import generate_article

output = generate_article(article, suggested_angle)
# ArticleOutput(
#     title="Python 包管理：从 pip 的屎山到 uv 的暴力美学",
#     content="...",
#     seo_tags=["Python", "uv", "包管理"]
# )
```

---

### 💾 Notion Sink - 存储器

**功能：** 将内容写入 Notion Database

**特性：**
- ✅ 支持长文本分块（2000 字符/段）
- ✅ 自动处理 Markdown 格式
- ✅ 错误重试机制
- ✅ 返回页面 URL

**使用：**
```python
from matrix.sinks.notion_sink import save_to_notion

url = save_to_notion(output_dict, database_id)
# 返回: "https://notion.so/xxx"
```

---

## 🎨 图文卡片渲染

### 功能

自动生成极客风格的 3:4 视觉卡片（1080x1440），适合：

- 📱 社交媒体分享（微信、微博、Twitter）
- 📊 内容预览图
- 🎨 品牌宣传

### 使用方法

```python
from matrix.renderers.image_renderer import generate_card

# 纯文字卡片
generate_card(
    title="Python 包管理：从 pip 的屎山到 uv 的暴力美学",
    content="核心观点：uv 用 Rust 重写了 pip，速度提升 10-100x...",
    output_path="output.png"
)

# 图文卡片（1-2 张图片）
generate_card(
    title="标题",
    content="内容",
    image_paths=["screenshot1.png", "screenshot2.png"],
    output_path="output.png"
)
```

### 设计特点

- 🎨 **深色极客风格**：#0A0A0A 背景 + #E0E0E0 文字
- 📐 **3:4 比例**：1080x1440（适合移动端）
- 🖼️ **动态布局**：支持 0-2 张图片自动排版
- 🎯 **Retina 渲染**：2x DPI 高清输出
- ⚡ **高性能**：Playwright 无头浏览器渲染

---

## 🔌 多源输入系统

除了 RSS，Matrix 还支持：

### 1. 本地笔记

将你的 Markdown 笔记转换为精美文章：

```python
from matrix.sources.note_source import NoteSource

source = NoteSource(notes_dir="~/notes")
articles = source.fetch()
```

**适用场景：**
- 📝 个人笔记整理
- 💡 灵感记录
- 📚 知识库管理

---

### 2. 手动输入

交互式输入，快速生成内容：

```python
from matrix.sources.manual_source import ManualSource

source = ManualSource()
articles = source.fetch()  # 交互式输入标题和内容
```

**适用场景：**
- 🎯 临时内容生成
- 🧪 测试和调试
- 📋 单篇文章处理

---

## ⚙️ 配置说明

### 环境变量

创建 `.env` 文件：

```env
# 必需
ANTHROPIC_API_KEY=sk-ant-your-key-here

# 可选（Notion 集成）
NOTION_API_TOKEN=ntn_your-token-here
NOTION_DATABASE_ID=your-database-id

# 可选（多源输入）
RSS_FEEDS=https://hnrss.org/frontpage,https://example.com/feed
NOTES_DIR=~/notes
MAX_ITEMS_PER_FEED=5
```

### 工作流配置

编辑 `src/matrix/config.py`：

```python
# 选择工作流模式
AGENT_MODE = False                      # 单 AI（默认）
AGENT_MODE = "basic"                    # 基础 Multi-Agent
AGENT_MODE = "langgraph"                # LangGraph 自主迭代
AGENT_MODE = "langgraph_enhanced"       # 增强版（推荐）
```

---

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 测试特定模块
uv run pytest tests/test_image_renderer.py -v

# 测试覆盖率
uv run pytest tests/ --cov=src/matrix --cov-report=html
```

### 测试套件

| 测试文件 | 描述 |
|---------|------|
| `test_image_renderer.py` | 图文卡片渲染测试 |
| `test_langgraph.py` | LangGraph 工作流测试 |
| `test_notion_tools.py` | Notion API 工具测试 |
| `test_graph.py` | 状态机测试 |

---

## 📚 文档

### 核心文档

- [架构设计](ARCHITECTURE.md) - 系统设计哲学和原则
- [贡献指南](CONTRIBUTING.md) - 如何参与项目开发

### 技术文档

- [AI 框架分析](docs/ai-frameworks-analysis.md) - 为什么选择原生实现
- [LangGraph 探索](docs/langgraph-exploration.md) - 自主 Agent 系统设计
- [LangGraph 严格架构](docs/langgraph-strict-architecture.md) - 状态机实现细节
- [Notion 工具指南](docs/notion-tools-guide.md) - Notion API 集成
- [图文卡片指南](docs/image-renderer-guide.md) - 卡片渲染器使用

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 贡献方式

- 🐛 报告 Bug
- 💡 提出新功能
- 📝 改进文档
- 🔧 提交代码

### 快速开始

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/YOUR_USERNAME/matrix.git

# 2. 创建特性分支
git checkout -b feature/amazing-feature

# 3. 提交更改
git commit -m "feat: add amazing feature"

# 4. 推送并创建 PR
git push origin feature/amazing-feature
```

详见 [贡献指南](CONTRIBUTING.md)

---

## 💬 社区

### 加入我们

<table>
<tr>
<td align="center" width="50%">

**微信交流群**

<img src="docs/images/wechat_qr.png" width="200" alt="微信群二维码">

扫码添加微信，备注「Matrix」

</td>
<td align="center" width="50%">

**Discord 社区**

[![Discord](https://img.shields.io/discord/YOUR_DISCORD_ID?color=7289da&label=Discord&logo=discord&logoColor=white)](https://discord.gg/YOUR_INVITE_CODE)

[点击加入 Discord](https://discord.gg/YOUR_INVITE_CODE)

</td>
</tr>
</table>

### 关注我们

- 🐦 Twitter: [@iridite_dev](https://twitter.com/iridite_dev)
- 📝 博客: [blog.iridite.dev](https://blog.iridite.dev)
- 📧 邮件: [hello@iridite.dev](mailto:hello@iridite.dev)

---

## 🗺️ Roadmap

### 近期计划（Q2 2025）

- [ ] 支持更多 AI 模型（OpenAI GPT-4、Google Gemini）
- [ ] Web UI 管理界面
- [ ] 定时任务调度
- [ ] 内容质量评分系统

### 中期计划（Q3-Q4 2025）

- [ ] 多语言支持（英文、日文）
- [ ] Docker 容器化部署
- [ ] 云端部署方案（AWS Lambda、Vercel）
- [ ] 插件系统

### 长期愿景

- [ ] 成为最��用的 AI 内容处理工具
- [ ] 构建活跃的开源社区
- [ ] 提供商业化 SaaS 服务

---

## 📊 项目统计

![Alt](https://repobeats.axiom.co/api/embed/YOUR_REPO_ID.svg "Repobeats analytics image")

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 🙏 致谢

### 核心依赖

- [Anthropic Claude](https://www.anthropic.com/) - 强大的 AI 模型
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent 工作流编排
- [uv](https://github.com/astral-sh/uv) - 极速 Python 包管理器
- [Playwright](https://playwright.dev/) - 浏览器自动化
- [Pydantic](https://pydantic.dev/) - 数据验证

### 灵感来源

- [n8n](https://n8n.io/) - 工作流自动化平台
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT) - 自主 AI Agent
- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用框架

### 贡献者

感谢所有为 Matrix 做出贡献的开发者！

<a href="https://github.com/iridite/matrix/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=iridite/matrix" />
</a>

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=iridite/matrix&type=Date)](https://star-history.com/#iridite/matrix&Date)

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个 ⭐ Star！**

Made with ❤️ by [Iridite](https://github.com/iridite)

[⬆ 回到顶部](#-matrix)

</div>
