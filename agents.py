"""Multi-Agent 协作系统"""
import os
from typing import List, Dict, Optional
from anthropic import Anthropic
from pydantic import BaseModel


class AgentMessage(BaseModel):
    """Agent 之间的消息"""
    role: str  # "writer-1", "critic", "editor", etc.
    content: str
    metadata: Optional[Dict] = None


class CollaborativeSession:
    """多 Agent 协作会话"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.messages: List[AgentMessage] = []
        self.shared_context = {}

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """添加消息到共享记忆"""
        msg = AgentMessage(role=role, content=content, metadata=metadata)
        self.messages.append(msg)
        return msg

    def get_conversation_history(self) -> str:
        """获取对话历史（供 Agent 查看）"""
        history = []
        for msg in self.messages:
            history.append(f"[{msg.role}]: {msg.content}")
        return "\n\n".join(history)


class WriterAgent:
    """写作 Agent - 生成内容"""

    def __init__(self, persona: str, client: Anthropic):
        self.persona = persona
        self.client = client
        self.name = f"writer-{persona}"

    def generate(self, article_data: dict, session: CollaborativeSession) -> str:
        """生成文章版本"""

        system_prompt = f"""你是一个专业的内容创作者，风格定位：{self.persona}

你的任务是根据原文信息生成一篇改写文章。

风格要求：
- 极简风格：简洁、直接、去除冗余
- 深度分析：挖掘深层逻辑、提供洞察
- 实用主义：注重可操作性、实用价值

输出格式：纯文本，不要 markdown 标记。"""

        user_prompt = f"""原文标题：{article_data.get('title', 'N/A')}
原文摘要：{article_data.get('summary', 'N/A')}
原文链接：{article_data.get('link', 'N/A')}

建议角度：{article_data.get('suggested_angle', '无')}

请生成一篇 {self.persona} 风格的改写文章。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        content = response.content[0].text
        session.add_message(self.name, content, {"persona": self.persona})
        return content


class CriticAgent:
    """评审 Agent - 评估各版本优劣"""

    def __init__(self, client: Anthropic):
        self.client = client
        self.name = "critic"

    def evaluate(self, versions: List[Dict], session: CollaborativeSession) -> Dict:
        """评估所有版本，返回评分和建议"""

        system_prompt = """你是一个专业的内容评审专家。

你的任务是评估多个文章版本，从以下维度打分（1-10分）：
1. 可读性
2. 信息密度
3. 独特视角
4. 实用价值

输出 JSON 格式：
{
  "scores": [
    {"version": 1, "readability": 8, "density": 7, "uniqueness": 6, "utility": 9, "total": 30},
    ...
  ],
  "recommendation": "推荐版本 X，因为...",
  "merge_suggestion": "可以融合版本 X 的开头 + 版本 Y 的论证..."
}"""

        versions_text = "\n\n---\n\n".join([
            f"版本 {i+1} ({v['persona']}):\n{v['content']}"
            for i, v in enumerate(versions)
        ])

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": f"请评估以下版本：\n\n{versions_text}"}]
        )

        evaluation = response.content[0].text
        session.add_message(self.name, evaluation)

        # 简单解析（实际应该用结构化输出）
        return {"evaluation": evaluation, "raw_response": response}


class JsonParserAgent:
    """JSON 解析 Agent - 专门处理格式化输出"""

    def __init__(self, client: Anthropic):
        self.client = client
        self.name = "json_parser"

    def parse_to_json(self, raw_content: str, article_data: dict) -> Dict:
        """将任意文本内容转换为标准 JSON 格式"""
        system_prompt = """你是一个 JSON 格式化专家。
你的任务是将给定的文章内容转换为严格的 JSON 格式。

输出要求：
1. 必须是纯 JSON，不要任何 markdown 标记
2. 不要 ```json 代码块包裹
3. 必须包含三个字段：title, content, seo_tags
4. content 保持 Markdown 格式
5. seo_tags 是字符串数组，3-5个标签

示例输出：
{"title": "标题", "content": "正文内容", "seo_tags": ["标签1", "标签2"]}"""

        user_prompt = f"""原文标题：{article_data.get('title', 'N/A')}
原文链接：{article_data.get('link', 'N/A')}

待格式化内容：
{raw_content}

请将上述内容转换为标准 JSON 格式。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=3000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        json_str = response.content[0].text.strip()

        # 尝试解析
        import json
        try:
            result = json.loads(json_str)
            print(f"  ✅ JSON Parser 成功解析")
            return result
        except Exception as e:
            print(f"  ⚠️  JSON Parser 也失败了: {e}")
            # 最终降级
            return {
                "title": article_data.get('title', 'AI 驱动的内容自动化')[:100],
                "content": raw_content,
                "seo_tags": ["AI", "自动化", "内容生产"]
            }


class EditorAgent:
    """编辑 Agent - 根据评审意见生成最终版本"""

    def __init__(self, client: Anthropic):
        self.client = client
        self.name = "editor"

    def finalize(self, versions: List[Dict], evaluation: str, session: CollaborativeSession) -> Dict:
        """生成最终版本"""

        system_prompt = """你是一个专业的内容编辑。

你的任务是根据评审意见，从多个版本中提取精华，生成最终版本。

输出 JSON 格式：
{
  "title": "最终标题",
  "content": "最终正文",
  "seo_tags": ["标签1", "标签2", "标签3"]
}"""

        versions_text = "\n\n---\n\n".join([
            f"版本 {i+1}:\n{v['content']}"
            for i, v in enumerate(versions)
        ])

        user_prompt = f"""评审意见：
{evaluation}

所有版本：
{versions_text}

请生成最终版本。"""

        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        final_content = response.content[0].text
        session.add_message(self.name, final_content)

        # 先尝试直接解析
        import json
        import re

        try:
            # 尝试提取 JSON（可能被 ```json ``` 包裹）
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', final_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = final_content

            result = json.loads(json_str)
            print(f"  ✅ Editor 直接解析成功")
            return result
        except Exception:
            print(f"  ⚠️  Editor 解析失败，调用 JSON Parser Agent...")
            # 调用专门的 JSON Parser Agent
            parser = JsonParserAgent(self.client)
            # 从 session 获取原始文章数据
            article_data = session.shared_context.get('article_data', {})
            return parser.parse_to_json(final_content, article_data)


def collaborative_generate(article_data: dict, api_key: Optional[str] = None) -> Dict:
    """
    多 Agent 协作生成文章

    流程：
    1. 3 个 Writer Agents 并行生成不同风格版本
    2. Critic Agent 评估所有版本
    3. Editor Agent 生成最终版本
    """
    client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    session = CollaborativeSession(api_key=api_key)

    # 保存原始文章数据到 session
    session.shared_context['article_data'] = article_data

    # 阶段 1: 并行生成
    print("🤖 阶段 1: 多 Agent 并行生成...")
    personas = ["极简风格", "深度分析", "实用主义"]
    versions = []

    for persona in personas:
        try:
            writer = WriterAgent(persona, client)
            content = writer.generate(article_data, session)
            versions.append({
                "persona": persona,
                "content": content
            })
            print(f"  ✅ {persona} 版本生成完成")
        except Exception as e:
            print(f"  ❌ {persona} 生成失败: {e}")

    if not versions:
        raise Exception("所有 Writer Agent 都失败了")

    # 阶段 2: 评审
    print("\n🤖 阶段 2: Critic Agent 评审...")
    critic = CriticAgent(client)
    evaluation_result = critic.evaluate(versions, session)
    print(f"  ✅ 评审完成")

    # 阶段 3: 编辑定稿
    print("\n🤖 阶段 3: Editor Agent 生成最终版本...")
    editor = EditorAgent(client)
    final_article = editor.finalize(versions, evaluation_result["evaluation"], session)
    print(f"  ✅ 最终版本生成完成\n")

    # 添加元数据
    final_article["original_url"] = article_data.get("link", "")
    final_article["agent_session"] = {
        "total_messages": len(session.messages),
        "versions_generated": len(versions)
    }

    return final_article
