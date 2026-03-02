# 多源输入系统 - 快速开始

## 新功能概览

Matrix 现在支持从多个来源获取内容：

- **RSS 源** - 技术趋势、行业动态
- **笔记源** - 个人思考、开发日志、踩坑记录
- **手动输入** - 临时快速发布

## 快速开始

### 1. 配置输入源

编辑 `.env` 文件：

```bash
# RSS 源（逗号分隔）
RSS_FEEDS=https://hnrss.org/frontpage,https://www.reddit.com/r/programming/.rss

# 笔记目录
NOTES_DIR=/home/user/notes

# 手动输入（可选）
MANUAL_TITLE=
MANUAL_CONTENT=
```

### 2. 运行多源模式

```bash
# 使用新的 main_graph.py
python main_graph.py
```

## 使用场景

### 场景 1：RSS + 笔记混合
```bash
# .env
RSS_FEEDS=https://hnrss.org/frontpage
NOTES_DIR=/home/user/dev-logs

# 运行
python main_graph.py
```

输出示例：
```
🚀 Matrix [多源输入 + LangGraph]

📡 抓取 RSS...
📝 读取笔记...

📊 共收集 12 篇文章

[1/12] [RSS] Show HN: I built a...
  ✅ SUCCESS
[2/12] [笔记] 为什么我切掉了 n8n
  ✅ SUCCESS
```

### 场景 2：纯笔记模式
```bash
# .env
RSS_FEEDS=
NOTES_DIR=/home/user/notes

# 运行
python main_graph.py
```

适合：
- 个人知识库整理
- 开发日志归档
- 思考笔记发布

### 场景 3：手动快速发布
```bash
export MANUAL_TITLE="CachyOS + niri 配置心得"
export MANUAL_CONTENT="最近折腾了 CachyOS..."

python main_graph.py
```

## 笔记格式建议

```markdown
# 为什么我切掉了 n8n

n8n 看起来很美好，但实际使用中发现：

1. 过度设计的 UI
2. 调试困难
3. 失去了对系统的控制权

最终我选择用 Python + uv 重写整个流程。

## 技术细节

使用 uv 管理依赖...
```

## 工作流程

```
多源输入 → LangGraph 状态机 → Sniper 过滤 → Writer 改写 → Notion 存储
```

所有输入源都会经过相同的 AI 处理流程：
1. **Sniper** - 过滤低质量内容
2. **Writer** - 改写成统一风格
3. **Notion** - 自动存储和分类

## 测试

```bash
# 运行测试
python tests/test_multi_source.py
```

测试覆盖：
- ✅ RSS 源抓取
- ✅ 笔记源读取
- ✅ 手动输入
- ✅ 状态机处理

## 扩展新源

在 `sources/` 目录创建新模块：

```python
# sources/twitter_source.py
def fetch_from_twitter(username: str) -> List[Dict]:
    tweets = []
    # ... 实现逻辑
    for tweet in tweets:
        tweet["source_type"] = "twitter"
    return tweets
```

在 `main_graph.py` 中添加：

```python
from sources.twitter_source import fetch_from_twitter

twitter_user = os.getenv("TWITTER_USERNAME", "")
if twitter_user:
    articles.extend(fetch_from_twitter(twitter_user))
```

## 完整文档

详见 [docs/multi-source-input.md](docs/multi-source-input.md)
