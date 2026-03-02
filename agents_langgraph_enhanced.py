"""增强版 LangGraph Agent - 集成 Notion 工具"""
import os
import json
from typing import TypedDict, Literal
from anthropic import Anthropic
from langgraph.graph import StateGraph, END, START
from tools.notion_tools import NotionTools, NOTION_TOOLS_DESCRIPTION


class AgentState(TypedDict):
    """Agent 共享状态"""
    # 输入
    article: dict  # 原文数据
    suggested_angle: str  # 建议角度
    database_id: str  # Notion Database ID

    # 工具调用结果
    notion_context: str  # Notion 查询结果

    # 中间状态
    research: str  # 市场分析
    draft: str  # 当前草稿
    critique: str  # 评审意见
    iteration: int  # 当前迭代次数

    # 输出
    final_output: dict  # 最终结果


class EnhancedLangGraphAgent:
    """增强版 LangGraph Agent - 支持 Notion 工具调用"""

    def __init__(self, api_key: str = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.notion_tools = NotionTools()
        self.max_iterations = 3

    def research_node(self, state: AgentState) -> AgentState:
        """研究节点 - 分析市场 + 查询 Notion 历史"""
        print("🔍 ResearchAgent: 分析市场 + 查询 Notion...")

        article = state["article"]
        db_id = state.get("database_id", os.getenv("NOTION_DATABASE_ID"))

        # 1. 查询 Notion 获取上下文
        notion_context = self._query_notion_context(article, db_id)

        # 2. 综合分析
        prompt = f"""你是一个市场分析专家。

原文标题：{article['title']}
原文摘要：{article.get('summary', 'N/A')[:500]}
建议角度：{state.get('suggested_angle', '无')}

Notion 历史数据：
{notion_context}

请分析：
1. 这个话题的市场热度如何？
2. 目标受众最关心什么？
3. 有哪些独特的切入角度？
4. 应该避免哪些陈词滥调？
5. 根据历史数据，如何避免重复？

给出简洁的分析（300字以内）。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        research = response.content[0].text
        print(f"  ✅ 分析完成: {research[:100]}...")

        return {
            **state,
            "research": research,
            "notion_context": notion_context,
            "iteration": 0
        }

    def _query_notion_context(self, article: dict, db_id: str) -> str:
        """查询 Notion 获取相关上下文"""
        try:
            # 1. 检查是否重复
            title = article['title']
            is_duplicate = self.notion_tools.check_duplicate(db_id, title)

            # 2. 获取最近主题
            recent_topics = self.notion_tools.get_recent_topics(db_id, days=7)

            # 3. 搜索相关内容
            search_results = self.notion_tools.search_pages(title[:50], max_results=3)

            # 构造上下文
            context_parts = []

            if is_duplicate:
                context_parts.append("⚠️ 警告：可能存在相似标题的文章")

            if recent_topics:
                context_parts.append(f"最近发布的主题（{len(recent_topics)}个）：")
                for topic in recent_topics[:10]:
                    context_parts.append(f"  - {topic}")

            if search_results:
                context_parts.append(f"\n相关文章（{len(search_results)}篇）：")
                for page in search_results:
                    context_parts.append(f"  - {page['title']}")

            return "\n".join(context_parts) if context_parts else "无相关历史数据"

        except Exception as e:
            print(f"  ⚠️ Notion 查询失败: {e}")
            return "Notion 查询失败"

    def writer_node(self, state: AgentState) -> AgentState:
        """写作节点 - 生成/重写内容"""
        iteration = state.get("iteration", 0)
        is_rewrite = iteration > 0

        if is_rewrite:
            print(f"✍️  WriterAgent: 重写内容 (第 {iteration} 次)...")
            critique = state.get("critique", "")
            prompt = f"""你是一个专业内容创作者。

原文标题：{state['article']['title']}
市场分析：{state['research']}
Notion 上下文：{state.get('notion_context', '无')}

之前的草稿：
{state['draft']}

评审意见：
{critique}

请根据评审意见重写内容，改进不足之处。

输出 JSON 格式：
{{
  "title": "改进后的标题",
  "content": "改进后的正文（Markdown 格式）",
  "seo_tags": ["标签1", "标签2", "标签3"],
  "original_url": "{state['article']['link']}"
}}"""
        else:
            print("✍️  WriterAgent: 生成初稿...")
            prompt = f"""你是一个专业内容创作者。

原文标题：{state['article']['title']}
原文摘要：{state['article'].get('summary', 'N/A')[:500]}
建议角度：{state['suggested_angle']}
市场分析：{state['research']}
Notion 上下文：{state.get('notion_context', '无')}

请基于以上信息，创作一篇高质量文章。

要求：
1. 标题吸引人，避免标题党
2. 内容有深度，避免陈词滥调
3. 结构清晰，使用 Markdown 格式
4. 避免与历史文章重复

输出 JSON 格式：
{{
  "title": "最终标题",
  "content": "完整正文（Markdown 格式）",
  "seo_tags": ["标签1", "标签2", "标签3"],
  "original_url": "{state['article']['link']}"
}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        draft = response.content[0].text
        print(f"  ✅ {'重写' if is_rewrite else '初稿'}完成")

        return {
            **state,
            "draft": draft,
            "iteration": iteration + 1
        }

    def critic_node(self, state: AgentState) -> AgentState:
        """评审节点 - 评估质量"""
        print("🎯 CriticAgent: 评审内容质量...")

        prompt = f"""你是一个严格的内容评审专家。

原文标题：{state['article']['title']}
市场分析：{state['research']}
Notion 上下文：{state.get('notion_context', '无')}

当前草稿：
{state['draft']}

请评审：
1. 标题是否吸引人？
2. 内容是否有深度？
3. 是否避免了陈词滥调？
4. 是否与历史文章重复？
5. 结构是否清晰？

如果质量不达标，请明确指出"不通过"并说明原因。
如果质量达标，请说"通过"。

评审意见（200字以内）："""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        critique = response.content[0].text
        print(f"  ✅ 评审完成: {critique[:100]}...")

        return {
            **state,
            "critique": critique
        }

    def editor_node(self, state: AgentState) -> AgentState:
        """编辑节点 - 最终润色"""
        print("📝 EditorAgent: 最终润色...")

        prompt = f"""你是一个专业编辑。

草稿：
{state['draft']}

评审意见：
{state.get('critique', '无')}

请进行最终润色，确保输出标准 JSON 格式：
{{
  "title": "最终标题",
  "content": "完整正文（Markdown 格式）",
  "seo_tags": ["标签1", "标签2", "标签3"],
  "original_url": "{state['article']['link']}"
}}

只输出 JSON，不要其他内容。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text

        # 解析 JSON
        try:
            # 尝试直接解析
            final_output = json.loads(content)
            print("  ✅ 润色完成")
        except json.JSONDecodeError:
            # 提取 JSON
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                final_output = json.loads(json_match.group())
                print("  ✅ 润色完成（提取 JSON）")
            else:
                print("  ⚠️ JSON 解析失败，使用原始内容")
                final_output = {
                    "title": state['article']['title'],
                    "content": content,
                    "seo_tags": [],
                    "original_url": state['article']['link']
                }

        return {
            **state,
            "final_output": final_output
        }

    def should_continue(self, state: AgentState) -> Literal["writer", "editor"]:
        """决策函数 - 是否需要重写"""
        critique = state.get("critique", "")
        iteration = state.get("iteration", 0)

        # 达到最大迭代次数，强制通过
        if iteration >= self.max_iterations:
            print(f"  ⚠️  已达最大迭代次数 ({self.max_iterations})，进入编辑")
            return "editor"

        # 检查是否需要重写
        needs_rewrite = any(keyword in critique for keyword in [
            "不通过", "需要改进", "问题", "不足", "建议修改"
        ])

        if needs_rewrite:
            print(f"  🔄 需要重写 (第 {iteration + 1}/{self.max_iterations} 次)")
            return "writer"

        # 评审通过
        print("  ✅ 评审通过，进入编辑")
        return "editor"

    def build_graph(self) -> StateGraph:
        """构建工作流图"""
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("research", self.research_node)
        workflow.add_node("writer", self.writer_node)
        workflow.add_node("critic", self.critic_node)
        workflow.add_node("editor", self.editor_node)

        # 添加边
        workflow.add_edge(START, "research")
        workflow.add_edge("research", "writer")
        workflow.add_edge("writer", "critic")

        # 条件边：根据评审结果决定是否重写
        workflow.add_conditional_edges(
            "critic",
            self.should_continue,
            {
                "writer": "writer",
                "editor": "editor"
            }
        )

        workflow.add_edge("editor", END)

        return workflow.compile()


def collaborative_generate_enhanced(article_data: dict) -> dict:
    """
    增强版协作生成 - 集成 Notion 工具

    Args:
        article_data: 包含 article 和 suggested_angle 的字典

    Returns:
        最终文章输出字典
    """
    system = EnhancedLangGraphAgent()
    graph = system.build_graph()

    # 准备初始状态
    initial_state: AgentState = {
        "article": article_data,
        "suggested_angle": article_data.get("suggested_angle", ""),
        "database_id": os.getenv("NOTION_DATABASE_ID", ""),
        "notion_context": "",
        "research": "",
        "draft": "",
        "critique": "",
        "iteration": 0,
        "final_output": {}
    }

    # 执行工作流
    print("\n🚀 启动增强版 LangGraph Agent 协作流程\n")
    result = graph.invoke(initial_state)

    return result["final_output"]
