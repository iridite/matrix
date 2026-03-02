# Notion 工具集成指南

## 概述

增强版 LangGraph Agent 集成了 Notion 工具，让 AI Agent 可以：
- 查询历史文章，避免重复发布
- 了解最近发布的主题，保持内容多样性
- 搜索相关内容，提供更好的上下文
- 基于历史数据做出更智能的决策

## 配置

### 1. 启用增强模式

编辑 `config.py`：
```python
AGENT_MODE = "langgraph_enhanced"
```

### 2. 配置环境变量

确保 `.env` 文件包含：
```bash
NOTION_API_KEY=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id
```

## Notion 工具功能

### 1. search_pages(query: str)
搜索 Notion 页面，返回匹配的页面列表。

**使用场景：**
- 查找相关主题的文章
- 检查是否已经写过类似内容

**示例：**
```python
results = notion_tools.search_pages("AI 最新进展", max_results=5)
# 返回: [{"id": "...", "title": "...", "url": "...", "created_time": "..."}]
```

### 2. query_database(database_id: str)
查询指定 Database 的内容。

**使用场景：**
- 获取所有已发布的文章
- 按条件过滤文章

**示例：**
```python
results = notion_tools.query_database(db_id, max_results=10)
# 返回: [{"id": "...", "properties": {...}, "url": "..."}]
```

### 3. get_page_content(page_id: str)
获取页面的完整内容（纯文本格式）。

**使用场景：**
- 分析已发布文章的内容
- 提取关键信息

**示例：**
```python
content = notion_tools.get_page_content(page_id)
# 返回: "# 标题\n\n段落内容..."
```

### 4. check_duplicate(database_id: str, title: str)
检查是否已存在相似标题的文章。

**使用场景：**
- 避免重复发布
- 在生成前检查

**示例：**
```python
is_duplicate = notion_tools.check_duplicate(db_id, "AI 最新进展")
# 返回: True/False
```

### 5. get_recent_topics(database_id: str, days: int = 7)
获取最近发布的主题列表。

**使用场景：**
- 了解最近的内容方向
- 保持主题多样性

**示例：**
```python
topics = notion_tools.get_recent_topics(db_id)
# 返回: ["主题1", "主题2", "主题3", ...]
```

## Agent 工作流

### Research Agent 的增强功能

在 Research 阶段，Agent 会自动：

1. **检查重复**
   ```
   ⚠️ 警告：可能存在相似标题的文章
   ```

2. **获取最近主题**
   ```
   最近发布的主题（10个）：
     - AI 技术突破
     - 机器学习应用
     - ...
   ```

3. **搜索相关内容**
   ```
   相关文章（3篇）：
     - 深度学习的未来
     - AI 伦理问题
     - ...
   ```

### 综合分析

Research Agent 会将 Notion 查询结果整合到市场分析中：

```
原文标题：AI 最新突破
Notion 历史数据：
  最近发布的主题（10个）：
    - AI 技术突破
    - 机器学习应用
  相关文章（3篇）：
    - 深度学习的未来

分析：
1. 市场热度：高
2. 受众关心：实际应用案例
3. 独特角度：从产品化角度切入
4. 避免陈词滥调：不要重复"AI 改变世界"
5. 避免重复：已有类似主题，需要新的切入点
```

## 测试工具

### 测试 Notion 连接

```bash
python test_notion_tools.py
```

输出示例：
```
🧪 测试 Notion 工具集

1️⃣ 测试搜索页面...
   找到 3 个页面:
   - AI 技术突破
   - 机器学习应用
   - 深度学习的未来

2️⃣ 测试查询 Database...
   找到 5 条记录:
   - 文章标题 1
   - 文章标题 2
   ...

✅ 所有测试完成
```

## 成本分析

| 操作 | API 调用 | 成本 |
|------|---------|------|
| 搜索页面 | 1 次 Notion API | 免费 |
| 查询 Database | 1 次 Notion API | 免费 |
| 获取页面内容 | 1 次 Notion API | 免费 |
| Research Agent | 1 次 Claude API | ~$0.003 |
| Writer Agent | 1-3 次 Claude API | ~$0.003-0.009 |
| Critic Agent | 1-3 次 Claude API | ~$0.003-0.009 |
| Editor Agent | 1 次 Claude API | ~$0.003 |

**总成本：** ~$0.012-0.024 / 篇文章（包含 Notion 查询）

## 最佳实践

### 1. 定期清理历史数据

Notion 查询会扫描最近 50 条记录，建议定期归档旧文章。

### 2. 优化搜索关键词

Research Agent 会自动提取标题关键词进行搜索，确保标题清晰。

### 3. 监控 API 限制

Notion API 有速率限制（3 次/秒），大批量处理时注意间隔。

### 4. 使用缓存

如果短时间内处理多篇文章，可以缓存 Notion 查询结果。

## 故障排查

### 问题 1: 401 Unauthorized

**原因：** Notion API Key 未配置或无效

**解决：**
1. 检查 `.env` 文件中的 `NOTION_API_KEY`
2. 确保 Integration 有访问 Database 的权限

### 问题 2: 查询返回空结果

**原因：** Database ID 错误或 Integration 无权限

**解决：**
1. 检查 `NOTION_DATABASE_ID` 是否正确
2. 在 Notion 中将 Database 共享给 Integration

### 问题 3: 重复检查不准确

**原因：** 简单的字符串匹配可能误判

**解决：**
- 当前使用包含匹配（`in` 操作）
- 可以升级为语义相似度检查（需要 embedding）

## 未来增强

### 计划中的功能

1. **语义搜索**
   - 使用 embedding 进行相似度匹配
   - 更准确的重复检测

2. **趋势分析**
   - 分析历史文章的阅读量
   - 识别热门主题

3. **自动标签**
   - 基于历史文章自动生成标签
   - 保持标签一致性

4. **内容推荐**
   - 推荐相关的历史文章
   - 建立内容关联

## 参考资料

- [Notion API 文档](https://developers.notion.com/)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Matrix 架构设计](../ARCHITECTURE.md)

---

*创建时间：2026-03-03*
