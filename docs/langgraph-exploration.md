# LangGraph 探索

## 什么是 LangGraph？

LangGraph 是 LangChain 团队开发的状态图框架，专门用于构建复杂的 Agent 工作流。

### 核心概念

1. **StateGraph** - 状态图，定义 Agent 的工作流
2. **Node** - 节点，每个节点是一个函数（Agent 的行为）
3. **Edge** - 边，定义节点之间的转换
4. **Conditional Edge** - 条件边，根据状态动态决定下一步
5. **State** - 共享状态，所有节点都可以读写

### 与当前方案对比

| 特性 | 当前原生实现 | LangGraph |
|------|-------------|-----------|
| 流程控制 | 硬编码 | 图结构 |
| 循环迭代 | 手动实现 | 内置支持 |
| 条件分支 | if/else | Conditional Edge |
| 状态管理 | 手动传递 | 自动管理 |
| 可视化 | 无 | 支持 |
| 调试 | print | 完整追踪 |

## 适合 Matrix 的场景

### 理想的 LangGraph 工作流

```
START
  ↓
ResearchAgent (分析市场情绪)
  ↓
WriterAgent (生成初稿)
  ↓
CriticAgent (评审)
  ↓ (条件判断)
  ├─ 满意 → EditorAgent → END
  └─ 不满意 → WriterAgent (重写，最多3次)
```

### 关键优势

1. **自动循环控制** - 不需要手动写 while 循环
2. **状态持久化** - 每个 Agent 的输出自动保存
3. **条件路由** - Critic 可以决定"重写"还是"通过"
4. **可视化调试** - 可以看到整个执行流程

## 实现计划

### Phase 1: 基础架构
- 安装 langgraph
- 定义 State 结构
- 创建基础节点

### Phase 2: Agent 节点
- ResearchAgent: 分析原文和市场
- WriterAgent: 生成内容
- CriticAgent: 评审质量
- EditorAgent: 最终润色

### Phase 3: 流程编排
- 定义节点之间的边
- 添加条件路由（重写逻辑）
- 设置最大迭代次数

### Phase 4: 集成测试
- 端到端测试
- 性能对比
- 成本分析

## 代码结构预览

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    article: dict
    research: str
    draft: str
    critique: str
    final_output: dict
    iteration: int

def research_node(state: AgentState) -> AgentState:
    # 调用 ResearchAgent
    pass

def writer_node(state: AgentState) -> AgentState:
    # 调用 WriterAgent
    pass

def critic_node(state: AgentState) -> AgentState:
    # 调用 CriticAgent
    pass

def should_rewrite(state: AgentState) -> str:
    # 决定是否重写
    if state["iteration"] >= 3:
        return "editor"
    if "需要改进" in state["critique"]:
        return "writer"
    return "editor"

# 构建图
workflow = StateGraph(AgentState)
workflow.add_node("research", research_node)
workflow.add_node("writer", writer_node)
workflow.add_node("critic", critic_node)
workflow.add_node("editor", editor_node)

workflow.add_edge("research", "writer")
workflow.add_edge("writer", "critic")
workflow.add_conditional_edges(
    "critic",
    should_rewrite,
    {
        "writer": "writer",  # 重写
        "editor": "editor"   # 通过
    }
)
workflow.add_edge("editor", END)

app = workflow.compile()
```

## 成本考虑

### API 调用次数

**当前方案（固定）：**
- 3 个 Writer + 1 个 Critic + 1 个 Editor = 5 次调用

**LangGraph 方案（动态）：**
- 最少：Research + Writer + Critic + Editor = 4 次
- 最多：Research + (Writer + Critic) × 3 + Editor = 8 次

### ��化策略

1. 设置最大迭代次数（如 3 次）
2. 使用更便宜的模型做 Research 和 Critic
3. 只在最终 Editor 使用最强模型

## 下一步

1. 安装 langgraph 依赖
2. 实现基础 State 和节点
3. 构建简单的循环流程
4. 测试并对比效果

---

*创建时间：2025-01-XX*
