# 多源输入系统

Matrix 现在支持从多个来源获取内容进行处理。

## 支持的输入源

### 1. RSS 源
从 RSS feeds 抓取文章。

**配置：**
```bash
RSS_FEEDS=https://hnrss.org/frontpage,https://www.reddit.com/r/programming/.rss
```

**特点：**
- 自动抓取最新文章
- 支持多个 feed（逗号分隔）
- 每个 feed 默认抓取 5 篇

### 2. 笔记源
从本地 Markdown 文件读取内容。

**配置：**
```bash
NOTES_DIR=/home/user/notes
```

**特点：**
- 递归扫描目录下所有 `.md` 文件
- 自动提取标题（第一行 `#` 标题）
- 保留完整内容用于 AI 处理
- 适合处理个人思考、开发日志、踩坑记录

**示例笔记结构：**
```
notes/
├── dev-logs/
│   ├── 2024-01-15-cachyos-setup.md
│   └── 2024-01-20-niri-config.md
├── thoughts/
│   ├── why-i-ditched-n8n.md
│   └── minimalist-workflow.md
└── problems/
    └── python-uv-issue.md
```

### 3. 手动输入源
直接通过环境变量输入单篇文章。

**配置：**
```bash
MANUAL_TITLE="为什么我切掉了 n8n"
MANUAL_CONTENT="长文内容..."
```

**特点：**
- 适合临时快速发布
- 可以通过脚本动态生成
- 不需要创建文件

## 工作流程

```
多源输入 → LangGraph 状态机 → Sniper 过滤 → Writer 改写 → Notion 存储
```

### 状态机流程

```
START → sniper → [条件判断]
                ├─ 通过 → writer → notion → END
                └─ 拒绝 → END
```

## 使用方法

### 方式 1：使用 RSS + 笔记
```bash
# .env 配置
RSS_FEEDS=https://hnrss.org/frontpage
NOTES_DIR=/home/user/notes

# 运行
python main_graph.py
```

### 方式 2：只使用笔记
```bash
# .env 配置
RSS_FEEDS=
NOTES_DIR=/home/user/notes

# 运行
python main_graph.py
```

### 方式 3：手动输入
```bash
# 临时设置环境变量
export MANUAL_TITLE="我的新文章"
export MANUAL_CONTENT="文章内容..."

python main_graph.py
```

## 输出格式

所有输入源都会被标准化为统一格式：

```python
{
    "title": "文章标题",
    "link": "原文链接或文件路径",
    "summary": "摘要（前 500 字符）",
    "published_date": "发布时间",
    "source_type": "rss/note/manual",
    "content": "完整内容（笔记/手动输入）"
}
```

## 扩展新的输入源

在 `sources/` 目录下创建新模块：

```python
# sources/twitter_source.py
def fetch_from_twitter(username: str) -> List[Dict]:
    """从 Twitter 抓取推文"""
    tweets = []
    # ... 实现逻辑
    for tweet in tweets:
        tweet["source_type"] = "twitter"
    return tweets
```

然后在 `main_graph.py` 中添加：

```python
from sources.twitter_source import fetch_from_twitter

# 在 main() 函数中
twitter_user = os.getenv("TWITTER_USERNAME", "")
if twitter_user:
    articles.extend(fetch_from_twitter(twitter_user))
```

## 实际应用场景

### 场景 1：技术博客自动化
- RSS 抓取 HN/Reddit 热门文章
- 笔记记录个人开发经验
- AI 改写成统一风格
- 自动发布到 Notion

### 场景 2：个人知识库
- 笔记记录日常思考
- AI 润色成正式文章
- 自动分类和打标签
- 构建个人知识图谱

### 场景 3：内容降维打击
- RSS 监控行业动态
- AI 快速生成深度分析
- 保持高频输出
- 建立内容护城河

## 注意事项

1. **笔记格式**：建议使用标准 Markdown 格式，第一行为 `# 标题`
2. **文件编码**：确保笔记文件使用 UTF-8 编码
3. **目录权限**：确保 Matrix 有读取笔记目录的权限
4. **内容质量**：Sniper 会过滤低质量内容，即使来自笔记源
