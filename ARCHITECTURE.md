# Matrix 项目结构

## 文件清单

```
matrix/
├── pyproject.toml          # uv 项目配置
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略规则
├── README.md               # 项目文档
├── main.py                 # 主流水线（48 行）
├── fetcher.py              # RSS 抓取模块
├── sniper.py               # AI 过滤模块
├── writer.py               # AI 改写模块
└── notion_sink.py          # Notion 存储模块
```

## 核心特性

### 1. 极简架构
- **零 Class 继承**：纯函数式管道
- **主循环 48 行**：绝对线性控制流
- **模块化设计**：每个模块单一职责

### 2. 绝对容错
```python
try:
    # 处理单篇文章
except KeyboardInterrupt:
    break  # Ctrl+C 瞬间退出
except Exception as e:
    print(f"❌ 失败: {e}")
    continue  # 不崩溃，继续下一篇
```

### 3. 物理截断
```python
# 防止 API 暴走
for entry in feed.entries[:max_items_per_feed]:
    # 只处理前 N 条
```

## 使用流程

### 初始化
```bash
# 1. 创建虚拟环境
uv venv
source .venv/bin/activate

# 2. 安装依赖
uv pip install -e .

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入：
# - ANTHROPIC_API_KEY
# - NOTION_API_KEY
# - NOTION_DATABASE_ID
```

### 运行
```bash
source .venv/bin/activate
python main.py
```

### 输出示例
```
🚀 Matrix 流水线启动

📡 [1/4] 抓取 RSS...
✅ 成功抓取 10 篇文章

--- 处理 1/10: OpenClaw Surpasses React...
🎯 [2/4] AI 过滤...
✅ 通过 [开源]: 从 GitHub Stars 增长速度切入
✍️  [3/4] AI 生成...
💾 [4/4] 写入 Notion...
✅ 已存入 Notion: OpenClaw：开源项目如何超越 React

--- 处理 2/10: New Python 3.14 Features...
🎯 [2/4] AI 过滤...
❌ 未通过: 纯版本更新，缺乏深度技术分析价值

✅ 流水线完成
```

## API 配额管理

### 成本估算（单次运行）
- **Fetcher**: 免费（RSS 解析）
- **Sniper**: ~10 篇 × $0.001 = $0.01
- **Writer**: ~3 篇通过 × $0.015 = $0.045
- **Notion**: 免费（API 调用）

**总计**: ~$0.055/次

### 优化策略
1. **物理截断**: `max_items_per_feed=5`（默认）
2. **过滤率**: Sniper 预期拒绝 70% 文章
3. **批量运行**: 建议每天 1-2 次

## 扩展建议

### 1. 添加缓存（防重复处理）
```python
# 在 main.py 添加
processed_urls = set()
if article['link'] in processed_urls:
    continue
processed_urls.add(article['link'])
```

### 2. 支持多个 Notion Database
```python
# 按分类路由
if filter_result.category == "AI":
    save_to_notion(output, AI_DB_ID)
elif filter_result.category == "开源":
    save_to_notion(output, OPENSOURCE_DB_ID)
```

### 3. 添加 Webhook 通知
```python
# 在 notion_sink.py 添加
import httpx
def notify_discord(title: str):
    httpx.post(DISCORD_WEBHOOK, json={"content": f"新文章: {title}"})
```

## 故障排查

### 问题：导入错误
```bash
# 确保在虚拟环境中
source .venv/bin/activate
uv pip install -e .
```

### 问题：API 超时
```python
# 在 sniper.py 和 writer.py 中调整
client = Anthropic(timeout=60.0)  # 默认 30s
```

### 问题：Notion 写入失败
- 检查 Database ID 是否正确
- 确认 Integration 有写入权限
- 验证 Database 属性名称匹配

## 性能指标

- **RSS 抓取**: ~2s/源
- **AI 过滤**: ~1s/篇
- **AI 改写**: ~8s/篇
- **Notion 写入**: ~0.5s/篇

**预期吞吐**: 10 篇文章 → 3 篇通过 → 总耗时 ~40s

## 许可证

MIT License - 自由使用、修改、分发
