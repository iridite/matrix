"""可视化 LangGraph 工作流"""
import sys
sys.path.insert(0, 'src')

import os
from dotenv import load_dotenv
from matrix.graph.graph_builder import MatrixWorkflow

load_dotenv()


def visualize_graph():
    """生成工作流图的可视化"""
    notion_db_id = os.getenv("NOTION_DATABASE_ID", "dummy-id")
    workflow_builder = MatrixWorkflow(notion_db_id)
    graph = workflow_builder.build_graph()

    # 打印图结构
    print("🔍 Matrix LangGraph 工作流结构\n")
    print("=" * 60)
    print("\n节点 (Nodes):")
    print("  1. sniper  - AI 过滤节点")
    print("  2. writer  - AI 写作节点")
    print("  3. notion  - Notion 存储节点")

    print("\n边 (Edges):")
    print("  START → sniper")
    print("  sniper → [条件判断]")
    print("    ├─ pass_filter=True  → writer")
    print("    └─ pass_filter=False → END")
    print("  writer → [条件判断]")
    print("    ├─ has_content=True  → notion")
    print("    └─ has_error=True    → END")
    print("  notion → END")

    print("\n状态 (State):")
    print("  - title: str")
    print("  - link: str")
    print("  - summary: str")
    print("  - published_date: str")
    print("  - pass_filter: bool")
    print("  - category: Optional[str]")
    print("  - reason: Optional[str]")
    print("  - suggested_angle: Optional[str]")
    print("  - draft_title: Optional[str]")
    print("  - draft_content: Optional[str]")
    print("  - seo_tags: Optional[list[str]]")
    print("  - notion_url: Optional[str]")
    print("  - error: Optional[str]")

    print("\n" + "=" * 60)
    print("\n工作流程示例:")
    print("\n1️⃣ 正常流程 (文章通过过滤):")
    print("   START → sniper → writer → notion → END")
    print("   状态变化: title → pass_filter=True → draft_content → notion_url")

    print("\n2️⃣ 过滤失败:")
    print("   START → sniper → END")
    print("   状态变化: title → pass_filter=False")

    print("\n3️⃣ 写作失败:")
    print("   START → sniper → writer → END")
    print("   状态变化: title → pass_filter=True → error")

    print("\n" + "=" * 60)

    # 尝试生成 Mermaid 图
    print("\n📊 Mermaid 流程图代码:\n")
    print("```mermaid")
    print("graph TD")
    print("    START([开始]) --> sniper[Sniper<br/>AI 过滤]")
    print("    sniper -->|通过| writer[Writer<br/>AI 写作]")
    print("    sniper -->|拒绝| END1([结束])")
    print("    writer -->|成功| notion[Notion<br/>存储]")
    print("    writer -->|失败| END2([结束])")
    print("    notion --> END3([结束])")
    print("    ")
    print("    style sniper fill:#f9f,stroke:#333,stroke-width:2px")
    print("    style writer fill:#bbf,stroke:#333,stroke-width:2px")
    print("    style notion fill:#bfb,stroke:#333,stroke-width:2px")
    print("```")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    visualize_graph()
