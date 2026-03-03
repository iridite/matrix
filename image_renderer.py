"""
图文卡片渲染器 - 极客审美的 3:4 视觉卡片生成

支持动态插入 1-2 张本地图片（代码截图、终端日志等）
使用 Playwright 渲染高清 PNG 卡片
"""
import base64
from pathlib import Path
from typing import List, Optional
from jinja2 import Template
from playwright.sync_api import sync_playwright


# ============================================================
# HTML/CSS 模板 - 深色极客风格
# ============================================================

CARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            width: 1080px;
            height: 1440px;
            background: #0A0A0A;
            color: #E0E0E0;
            font-family: 'SF Mono', 'Consolas', 'Monaco', monospace;
            display: flex;
            flex-direction: column;
            padding: 60px;
        }

        .title {
            font-size: 48px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 40px;
            color: #FFFFFF;
            letter-spacing: -0.5px;
        }

        .images-container {
            flex: 1;
            display: flex;
            gap: 20px;
            margin-bottom: 40px;
            {% if image_count == 1 %}
            justify-content: center;
            align-items: center;
            {% elif image_count == 2 %}
            flex-direction: row;
            {% endif %}
        }

        .image-wrapper {
            {% if image_count == 1 %}
            width: 100%;
            max-height: 800px;
            {% elif image_count == 2 %}
            flex: 1;
            {% endif %}
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .image-wrapper img {
            max-width: 100%;
            max-height: 100%;
            border-radius: 8px;
            border: 1px solid #333;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
            object-fit: contain;
        }

        .content {
            font-size: 28px;
            line-height: 1.6;
            color: #B0B0B0;
            margin-top: auto;
        }

        .content strong {
            color: #FFFFFF;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="title">{{ title }}</div>

    {% if images %}
    <div class="images-container">
        {% for img_data in images %}
        <div class="image-wrapper">
            <img src="data:image/png;base64,{{ img_data }}" alt="Screenshot">
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="content">{{ content | safe }}</div>
</body>
</html>
"""


# ============================================================
# 核心函数
# ============================================================

def encode_image_to_base64(image_path: str) -> str:
    """
    将本地图片转换为 Base64 编码

    Args:
        image_path: 图片文件路径

    Returns:
        Base64 编码字符串
    """
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_card(
    title: str,
    content: str,
    image_paths: Optional[List[str]] = None,
    output_path: str = "output_card.png"
) -> str:
    """
    生成 3:4 图文卡片

    Args:
        title: 卡片标题
        content: 核心观点文字（支持 HTML 标签）
        image_paths: 本地图片路径列表（最多 2 张）
        output_path: 输出 PNG 路径

    Returns:
        生成的图片路径
    """
    # 处理图片
    images_base64 = []
    if image_paths:
        for path in image_paths[:2]:  # 最多 2 张
            if Path(path).exists():
                images_base64.append(encode_image_to_base64(path))
            else:
                print(f"⚠️  图片不存在: {path}")

    # 渲染 HTML
    template = Template(CARD_TEMPLATE)
    html = template.render(
        title=title,
        content=content,
        images=images_base64,
        image_count=len(images_base64)
    )

    # 使用 Playwright 渲染
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1080, "height": 1440},
            device_scale_factor=2  # Retina 高清
        )

        # 加载 HTML 并等待资源加载完成
        page.set_content(html, wait_until="networkidle")

        # 截图
        page.screenshot(path=output_path, full_page=True)
        browser.close()

    print(f"✅ 卡片已生成: {output_path}")
    return output_path


# ============================================================
# LangGraph 节点适配
# ============================================================

def node_render_image(state: dict) -> dict:
    """
    LangGraph 节点 - 渲染图文卡片

    从 state 中读取:
        - draft_title: 文章标题
        - draft_content: 文章内容（取前 200 字作为摘要）
        - local_media_list: 本地图片路径列表

    返回:
        - final_card_path: 生成的卡片路径
    """
    try:
        title = state.get("draft_title", "无标题")
        content = state.get("draft_content", "")

        # 提取前 200 字作为卡片内容
        summary = content[:200] + "..." if len(content) > 200 else content

        # 获取图片路径
        image_paths = state.get("local_media_list", [])

        # 生成卡片
        output_path = f"cards/{title[:20]}.png"
        Path("cards").mkdir(exist_ok=True)

        card_path = generate_card(
            title=title,
            content=summary,
            image_paths=image_paths,
            output_path=output_path
        )

        return {"final_card_path": card_path}

    except Exception as e:
        print(f"❌ 卡片生成失败: {e}")
        return {"error": f"卡片生成失败: {str(e)}"}


# ============================================================
# 测试接口
# ============================================================

if __name__ == "__main__":
    # 测试用例
    test_title = "Python 包管理：从 pip 的屎山到 uv 的暴力美学"
    test_content = """
    <strong>核心观点：</strong>uv 用 Rust 重写了整个 Python 包管理工具链，
    速度提升 10-100 倍，彻底解决了 pip 的依赖地狱问题。
    """

    # 创建测试图片（如果有的话）
    test_images = []  # 替换为实际图片路径，例如: ["screenshot1.png", "screenshot2.png"]

    generate_card(
        title=test_title,
        content=test_content,
        image_paths=test_images,
        output_path="test_card.png"
    )
