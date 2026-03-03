"""Matrix - 全自动内容降维打击流水线"""

__version__ = "0.1.0"

# 导出核心接口
from matrix.core.fetcher import fetch_feeds
from matrix.core.sniper import filter_article
from matrix.core.writer import generate_article
from matrix.sinks.notion_sink import save_to_notion
from matrix.renderers.image_renderer import generate_card, node_render_image
from matrix.graph.graph_builder import build_graph, process_single_article

__all__ = [
    "fetch_feeds",
    "filter_article",
    "generate_article",
    "save_to_notion",
    "generate_card",
    "node_render_image",
    "build_graph",
    "process_single_article",
]
