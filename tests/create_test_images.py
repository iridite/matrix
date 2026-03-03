import sys
sys.path.insert(0, 'src')

"""
生成测试用的占位图片
"""
from PIL import Image, ImageDraw, ImageFont

def create_test_screenshot(text: str, output_path: str, size=(800, 600)):
    """创建测试截图"""
    # 创建深色背景
    img = Image.new('RGB', size, color='#1E1E1E')
    draw = ImageDraw.Draw(img)

    # 添加文字
    try:
        font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSansMono.ttf", 40)
    except OSError:
        font = ImageFont.load_default()

    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    # 绘制文字
    draw.text((x, y), text, fill='#00FF00', font=font)

    # 添加边框
    draw.rectangle([(10, 10), (size[0]-10, size[1]-10)], outline='#333333', width=2)

    img.save(output_path)
    print(f"✅ 生成测试图片: {output_path}")


if __name__ == "__main__":
    from pathlib import Path

    Path("test_assets").mkdir(exist_ok=True)

    create_test_screenshot("$ uv add httpx\n✓ Installed in 0.5s", "test_assets/screenshot1.png")
    create_test_screenshot("import httpx\nresponse = httpx.get(url)", "test_assets/screenshot2.png")
