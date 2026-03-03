"""LangGraph 版本的 Multi-Agent 协作系统"""
import os
from typing import TypedDict, Literal
from anthropic import Anthropic
from langgraph.graph import StateGraph, END, START


class AgentState(TypedDict):
    """Agent 共享状态"""
    # 输入
    article: dict  # 原文数据
    suggested_angle: str  # 建议角度

    # 中间状态
    research: str  # 市场分析
    draft: str  # 当前草稿
    critique: str  # 评审意见
    iteration: int  # 当前迭代次数

    # 输出
    final_output: dict  # 最终结果


class LangGraphAgentSystem:
    """基于 LangGraph 的自主协作 Agent 系统"""

    def __init__(self, api_key: str = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.max_iterations = 3

    def research_node(self, state: AgentState) -> AgentState:
        """研究节点 - 分析市场情绪和热点"""
        print("🔍 ResearchAgent: 分析市场情绪...")

        article = state["article"]
        prompt = f"""你是一个市场分析专家。

原文标题：{article['title']}
原文摘要：{article.get('summary', 'N/A')[:500]}
建议角度：{state.get('suggested_angle', '无')}

请分析：
1. 这个话题的市场热度如何？
2. 目标受众最关心什么？
3. 有哪些独特的切入角度？
4. 应该避免哪些陈词滥调？

给出简洁的分析（200字以内）。"""

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
            "iteration": 0
        }

    def writer_node(self, state: AgentState) -> AgentState:
        """写作节点 - 生成或重写内容"""
        iteration = state.get("iteration", 0)
        is_rewrite = iteration > 0

        if is_rewrite:
            print(f"✍️  WriterAgent: 第 {iteration + 1} 次重写...")
        else:
            print("✍️  WriterAgent: 生成初稿...")

        article = state["article"]
        research = state.get("research", "")
        critique = state.get("critique", "")

        # 构建 prompt
        base_prompt = f"""你是一个专业的内容创作者。

原文标题：{article['title']}
原文摘要：{article.get('summary', 'N/A')[:500]}

市场分析：
{research}
"""

        if is_rewrite and critique:
            base_prompt += f"""
上一版本的问题：
{critique}

请根据评审意见重写，改进不足之处。
"""

        base_prompt += """
请生成一篇改写文章（800-1200字），要求：
1. 标题吸引人，有独特角度
2. 内容深度足够，避免空洞
3. 语言简洁有力，符合 Iridite 风格
4. 结构清晰，逻辑连贯

直接输出文章内容，不要额外说明。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": base_prompt}]
        )

        draft = response.content[0].text
        print(f"  ✅ {'重写' if is_rewrite else '初稿'}完成")

        return {
            **state,
            "draft": draft,
            "iteration": iteration + 1
        }

    def critic_node(self, state: AgentState) -> AgentState:
        """评审节点 - 评估内容质量"""
        print("🔎 CriticAgent: 评审内容...")

        draft = state["draft"]
        research = state["research"]

        prompt = f"""你是一个严格的内容评审专家。

市场分析：
{research}

待评审文章：
{draft}

请评估：
1. 标题是否吸引人？
2. 内容深度是否足够？
3. 是否有独特见解？
4. 语言是否简洁有力？
5. 是否符合市场需求？

如果质量优秀，回复"通过"。
如果需要改进，明确指出问题（100字以内）。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        critique = response.content[0].text
        print(f"  ✅ 评审完成: {critique[:50]}...")

        return {
            **state,
            "critique": critique
        }

    def editor_node(self, state: AgentState) -> AgentState:
        """编辑节点 - 最终润色和格式化"""
        print("📝 EditorAgent: 最终润色...")

        draft = state["draft"]
        article = state["article"]

        prompt = f"""你是一个专业编辑。

原文链接：{article.get('link', 'N/A')}

文章内容：
{draft}

请输出标准 JSON 格式（不要 markdown 代码块）：
{{"title": "最终标题", "content": "最终正文（Markdown格式）", "seo_tags": ["标签1", "标签2", "标签3"]}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text.strip()

        # 解析 JSON
        import json
        import re

        try:
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = content

            final_output = json.loads(json_str)
            print(f"  ✅ 润色完成: {final_output['title']}")
        except Exception as e:
            print(f"  ⚠️  JSON 解析失败: {e}")
            final_output = {
                "title": article.get('title', 'AI 驱动的内容自动化')[:100],
                "content": draft,
                "seo_tags": ["AI", "自动化", "内容生产"]
            }

        return {
            **state,
            "final_output": final_output
        }

    def should_continue(self, state: AgentState) -> Literal["writer", "editor"]:
        """条件路由 - 决定是重写还是通过"""
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

        # 条件边：根据评审结果决定下一步
        workflow.add_conditional_edges(
            "critic",
            self.should_continue,
            {
                "writer": "writer",  # 重写
                "editor": "editor"   # 通过
            }
        )

        workflow.add_edge("editor", END)

        return workflow.compile()

    def generate(self, article_data: dict) -> dict:
        """生成文章"""
        print("\n🚀 启动 LangGraph Agent 系统...\n")

        # 构建图
        app = self.build_graph()

        # 初始状态
        initial_state = {
            "article": article_data,
            "suggested_angle": article_data.get("suggested_angle", ""),
            "research": "",
            "draft": "",
            "critique": "",
            "iteration": 0,
            "final_output": {}
        }

        # 执行工作流
        final_state = app.invoke(initial_state)

        print("\n✅ LangGraph 工作流完成\n")

        return final_state["final_output"]


def collaborative_generate_langgraph(article_data: dict, api_key: str = None) -> dict:
    """LangGraph 版本的协作生成函数"""
    system = LangGraphAgentSystem(api_key=api_key)
    return system.generate(article_data)
