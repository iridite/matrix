"""
测试图文卡片渲染器

测试场景：
1. 纯文字卡片（无图片）
2. 单图卡片
3. 双图卡片
"""
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from image_renderer import generate_card


def test_text_only_card():
    """测试纯文字卡片"""
    print("\n=== 测试 1: 纯文字卡片 ===")

    title = "Python 包管理：从 pip 的屎山到 uv 的暴力美学"
    content = """
    <strong>核心观点：</strong>uv 用 Rust 重写了整个 Python 包管理工具链，
    速度提升 10-100 倍，彻底解决了 pip 的依赖地狱问题。
    <br><br>
    不再需要 virtualenv、pip-tools、poetry 这些工具的复杂组合，
    一个 uv 搞定所有场景。
    """

    output = generate_card(
        title=title,
        content=content,
        image_paths=None,
        output_path="test_outputs/card_text_only.png"
    )

    print(f"✅ 生成成功: {output}")


def test_single_image_card():
    """测试单图卡片"""
    print("\n=== 测试 2: 单图卡片 ===")

    title = "CachyOS + Niri：极简 Wayland 桌面配置"
    content = """
    <strong>终端截图展示：</strong>Niri 的平铺窗口管理器配合 CachyOS 的性能优化，
    打造出极致流畅的开发环境。
    """

    # 如果有测试图片，替换这里的路径
    test_image = "test_assets/screenshot1.png"

    if Path(test_image).exists():
        output = generate_card(
            title=title,
            content=content,
            image_paths=[test_image],
            output_path="test_outputs/card_single_image.png"
        )
        print(f"✅ 生成成功: {output}")
    else:
        print(f"⚠️  测试图片不存在: {test_image}")
        print("   请将测试图片放到 test_assets/ 目录")


def test_double_image_card():
    """测试双图卡片"""
    print("\n=== 测试 3: 双图卡片 ===")

    title = "n8n 的混乱 UI vs 代码的优雅"
    content = """
    <strong>对比展示：</strong>左图是 n8n 复杂的节点连线，
    右图是简洁的 Python 代码实现相同功能。
    """

    test_images = [
        "test_assets/screenshot1.png",
        "test_assets/screenshot2.png"
    ]

    existing_images = [img for img in test_images if Path(img).exists()]

    if len(existing_images) >= 2:
        output = generate_card(
            title=title,
            content=content,
            image_paths=existing_images,
            output_path="test_outputs/card_double_image.png"
        )
        print(f"✅ 生成成功: {output}")
    else:
        print("⚠️  需要至少 2 张测试图片")
        print("   请将测试图片放到 test_assets/ 目录")


if __name__ == "__main__":
    # 创建输出目录
    Path("test_outputs").mkdir(exist_ok=True)
    Path("test_assets").mkdir(exist_ok=True)

    # 运行测试
    test_text_only_card()
    test_single_image_card()
    test_double_image_card()

    print("\n=== 所有测试完成 ===")
    print("查看生成的卡片: test_outputs/")
