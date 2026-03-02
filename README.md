# Matrix - 全自动内容降维打击流水线

> 取代臃肿的 n8n，用纯 Python 实现绝对线性的内容处理管道

## 架构理念

- **极小执行力**：拒绝过度设计，函数式管道，零 Class 继承树
- **绝对容错**：单篇失败不崩溃，Ctrl+C 瞬间中断
- **高租售比**：每行代码都有明确价值

## 流水线

```
RSS 抓取 → AI 过滤 → AI 改写 → Notion 存储
(fetcher) → (sniper) → (writer) → (notion_sink)
```

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

### 3. 运行

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行主程序
python main.py
```

## 模块说明

### `fetcher.py` - RSS 抓取器
- 输入：RSS/Atom URL 列表
- 输出：标准化文章字典
- 特性：物理截断（防 API 暴走）

### `sniper.py` - AI 预处理网关
- 模型：Claude 3.5 Haiku（极速）
- 任务：判断文章是否值得改写
- 输出：`FilterResult` (Pydantic 严格校验)

### `writer.py` - AI 核心加工厂
- 模型：Claude 3.5 Sonnet（高能力）
- 任务：生成降维打击式长文
- 输出：`ArticleOutput` (标题/正文/SEO)

### `notion_sink.py` - Notion 存储器
- 协议：Notion API (httpx)
- 任务：写入 Database 并记录时间戳

## Notion Database 结构

需要创建一个包含以下属性的 Database：

| 属性名 | 类型 |
|--------|------|
| 标题 | Title |
| 原文链接 | URL |
| SEO标签 | Multi-select |
| 创建时间 | Date |

## 容错机制

- 单个 RSS 源失败 → 打印日志，继续下一个
- 单篇文章解析失败 → 跳过，不影响其他
- API 调用超时 → 捕获异常，标记失败
- Ctrl+C 中断 → 立即退出，不等待

## 依赖

- `feedparser` - RSS/Atom 解析
- `httpx` - 异步/同步 HTTP 客户端
- `pydantic` - 数据结构校验
- `anthropic` - Claude API SDK
- `python-dotenv` - 环境变量管理

## License

MIT
