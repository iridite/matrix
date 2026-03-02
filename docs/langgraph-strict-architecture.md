# LangGraph 严格架构实现

## 架构概览

严格按照 LangGraph 最佳实践重构 Matrix 流水线：

```
┌─────────────────────────────────────────────────────────┐
│                    ArticleState                         │
│  (全局状态 - TypedDict)                                  │
│  - title, link, summary, published_date                 │
│  - pass_filter, category, reason, suggested_angle       │
│  - draft_title, draft_content, seo_tags                 │
│  - notion_url, error                                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   StateGraph                            │
│                                                         │
│  START → sniper → [should_write?]                       │
│                   ├─ True  → writer → notion → END      │
│                   └─ False → END                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  main_graph.py                          │
│  (调度中心)                                              │
│  for article in articles:                               │
│      result = process_single_article(article)           │
│      print([SUCCESS] / [SKIP] / [ERROR])                │
└─────────────────────────────────────────────────────────┘
```

## 核心文件

### 1. graph_builder.py (状态机核心)

**职责：**
- 定义全局状态 `ArticleState`
- 实现节点包装器（不修改原模块逻辑）
- 实现路由函数
- 组装 StateGraph

**关键设计：**

#### 状态定义
```python
class ArticleState(TypedDict):
    # 原始数据
    title: str
    link: str
    summary: str
    published_date: str

    # Sniper 处理结果
    pass_filter: bool
    category: Optional[str]
    reason: Optional[str]
    suggested_angle: Optional[str]

    # Writer 处理结果
    draft_title: Optional[str]
    draft_content: Optional[str]
    seo_tags: Optional[list[str]]

    # Notion 处理结果
    notion_url: Optional[str]
    error: Optional[str]
```

#### 节点包装器
```python
def node_sniper(state: ArticleState) -> dict:
    """包装 sniper.py - 只返回要更新的字段"""
    article = {"title": state["title"], ...}
    result = filter_article(article)  # 调用原模块
    return {
        "pass_filter": result.pass_filter,
        "category": result.category,
        ...
    }
```

**原则：**
- ✅ 节点函数只返回要更新的字段（部分状态）
- ✅ 不修改原模块的 LLM 调用和 Prompt
- ✅ 错误处理在节点内完成

#### 路由函数
```python
def should_write(state: ArticleState) -> Literal["writer", "END"]:
    """核心路由 - 决定是否写作"""
    return "writer" if state.get("pass_filter") else "END"
```

#### 图组装
```python
def build_graph() -> StateGraph:
    workflow = StateGraph(ArticleState)

    # 添加节点
    workflow.add_node("sniper", node_sniper)
    workflow.add_node("writer", node_writer)
    workflow.add_node("notion", node_notion)

    # 设置入口点
    workflow.set_entry_point("sniper")

    # 条件边
    workflow.add_conditional_edges(
        "sniper",
        should_write,
        {"writer": "writer", "END": END}
    )

    # 普通边
    workflow.add_edge("writer", "notion")
    workflow.add_edge("notion", END)

    return workflow.compile()
```

### 2. main_graph.py (调度中心)

**职责：**
- 抓取 RSS 文章列表
- 遍历处理每篇文章
- 打印极简日志
- 错误隔离

**实现：**
```python
def main():
    print("🚀 Matrix [LangGraph]\n")

    # 抓取 RSS
    articles = fetch_feeds(RSS_FEEDS, max_items_per_feed=MAX_ITEMS)

    # 遍历处理
    for idx, article in enumerate(articles, 1):
        try:
            result = process_single_article(article)

            # 冷酷简短的日志
            if result.get("notion_url"):
                print(f"[{idx}] SUCCESS: {result['draft_title'][:50]}")
            elif result.get("error"):
                print(f"[{idx}] ERROR: {result['error']}")
            else:
                print(f"[{idx}] SKIP: {result.get('reason', 'N/A')}")

        except KeyboardInterrupt:
            print("\n[ABORT] 用户中断")
            break
        except Exception as e:
            print(f"[{idx}] FAIL: {str(e)}")
            continue

    print("\n✅ 完成")
```

**日志格式：**
- `[1] SUCCESS: 深度解析：AI 技术突破`
- `[2] SKIP: 内容不符合要求`
- `[3] ERROR: Writer 失败: API timeout`
- `[4] FAIL: Unexpected error`

## 工作流程

### 场景 1: 文章通过过滤

```
初始状态:
{
    "title": "AI 技术突破",
    "pass_filter": False,
    "draft_title": None,
    "notion_url": None
}

↓ node_sniper

{
    "pass_filter": True,
    "category": "技术",
    "suggested_angle": "从产品化角度分析"
}

↓ should_write → "writer"

↓ node_writer

{
    "draft_title": "深度解析：AI 技术突破",
    "draft_content": "# 内容...",
    "seo_tags": ["AI", "技术"]
}

↓ node_notion

{
    "notion_url": "已保存"
}

↓ END

日志: [1] SUCCESS: 深度解析：AI 技术突破
```

### 场景 2: 文章未通过过滤

```
初始状态:
{
    "title": "天气预报",
    "pass_filter": False
}

↓ node_sniper

{
    "pass_filter": False,
    "reason": "内容不符合要求"
}

↓ should_write → "END"

↓ END (跳过 writer 和 notion)

日志: [2] SKIP: 内容不符合要求
```

### 场景 3: 写作失败

```
初始状态 → node_sniper (通过) → node_writer (失败)

{
    "pass_filter": True,
    "error": "Writer 失败: API timeout"
}

↓ node_notion (检测到 error，跳过保存)

日志: [3] ERROR: Writer 失败: API timeout
```

## 关键设计原则

### 1. 状态不可变
- 节点函数返回部分状态（dict）
- LangGraph 自动合并到全局状态
- 不直接修改 state 参数

### 2. 节点职责单一
- `node_sniper` - 只负责过滤判断
- `node_writer` - 只负责内容生成
- `node_notion` - 只负责存储

### 3. 路由逻辑清晰
- `should_write` - 唯一的条件路由
- 基于 `pass_filter` 字段决策
- 返回明确的字符串标识

### 4. 错误隔离
- 节点内部捕获异常，返回 `error` 字段
- main.py 中 try-except 确保单篇失败不影响整体
- 日志清晰标识错误类型

### 5. 极简日志
- 不打印冗余信息
- 使用 `[SUCCESS]` / `[SKIP]` / `[ERROR]` / `[FAIL]` 标识
- 标题截断到 50 字符

## 使用方法

### 运行流水线
```bash
python main_graph.py
```

### 测试（模拟��本）
```bash
python test_strict_graph.py
```

### 预期输出
```
🚀 Matrix [LangGraph]

[1] SUCCESS: 深度解析：AI 技术突破
[2] SKIP: 内容不符合要求
[3] SUCCESS: 机器学习的未来趋势
[4] ERROR: Writer 失败: API timeout
[5] SKIP: 内容质量不足

✅ 完成
```

## 扩展性

### 添加新节点
```python
def node_translator(state: ArticleState) -> dict:
    """翻译节点"""
    # 实现翻译逻辑
    return {"translated_content": text}

# 在 build_graph 中添加
workflow.add_node("translator", node_translator)
workflow.add_edge("writer", "translator")
workflow.add_edge("translator", "notion")
```

### 添加新路由
```python
def should_translate(state: ArticleState) -> Literal["translator", "notion"]:
    """决定是否翻译"""
    if state.get("category") == "国际":
        return "translator"
    return "notion"

workflow.add_conditional_edges("writer", should_translate, {...})
```

### 添加重试逻辑
```python
def should_retry(state: ArticleState) -> Literal["writer", "notion"]:
    """决定是否重试"""
    retry_count = state.get("retry_count", 0)
    if state.get("error") and retry_count < 3:
        return "writer"
    return "notion"
```

## 对比原始架构

| 特性 | 原始 main.py | LangGraph 严格架构 |
|------|-------------|-------------------|
| 状态管理 | 分散在变量中 | 集中在 ArticleState |
| 流程控制 | if-else 嵌套 | 条件边路由 |
| 节点复用 | 无 | 可独立测试和复用 |
| 错误处理 | try-except 混杂 | 节点内部 + 调度层 |
| 可视化 | 无 | 清晰的图结构 |
| 扩展性 | 需修改主逻辑 | 添加节点即可 |
| 日志 | 冗长 | 极简冷酷 |

## 测试结果

```
🧪 测试严格架构版本

测试 1: AI 文章
  通过: True
  标题: 深度解析：AI 技术突破
  Notion: 已保存

测试 2: 无关文章
  通过: False
  原因: 内容不符合要求
  标题: None (应为 None)
  Notion: None (应为 None)

✅ 测试完成
```

## 总结

严格架构版本的核心优势：

1. **清晰的状态管理** - 所有状态集中在 ArticleState
2. **单一职责节点** - 每个节点只做一件事
3. **明确的路由逻辑** - should_write 是唯一的决策点
4. **完美的错误隔离** - 单篇失败不影响整体
5. **极简的日志输出** - 冷酷、简短、清晰
6. **强大的扩展性** - 添加节点不影响现有逻辑

---

*创建时间：2026-03-03*
