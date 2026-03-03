# 图文卡片渲染器使用指南

## 功能概述

`image_renderer.py` 提供极客风格的 3:4 视觉卡片生成功能，支持：
- 深色模式（#0A0A0A 背景）
- 动态插入 1-2 张本地图片
- Retina 高清渲染（2x device scale）
- Base64 图片注入（跨平台兼容）

## 快速开始

### 1. 基础用法

```python
from image_renderer import generate_card

# 纯文字卡片
generate_card(
    title="Python 包管理：从 pip 的屎山到 uv 的暴力美学",
    content="<strong>核心观点：</strong>uv 用 Rust 重写了整个工具链...",
    output_path="output.png"
)

# 单图卡片
generate_card(
    title="CachyOS + Niri 配置",
    content="终端截图展示...",
    image_paths=["screenshot.png"],
    output_path="output.png"
)

# 双图卡片
generate_card(
    title="n8n vs 代码对比",
    content="左图是 n8n，右图是代码...",
    image_paths=["n8n.png", "code.png"],
    output_path="output.png"
)
```

### 2. LangGraph 集成

在 `graph_builder.py` 中添加渲染节点：

```python
from image_renderer import node_render_image

# 添加节点
workflow.add_node("render", node_render_image)

# 添加边
workflow.add_edge("writer", "render")
workflow.add_edge("render", "notion")
```

状态字段：
- `local_media_list`: 输入图片路径列表
- `final_card_path`: 输出卡片路径

### 3. 运行测试

```bash
# 创建测试图片目录
mkdir -p test_assets

# 放入测试图片（可选）
cp your_screenshot.png test_assets/screenshot1.png

# 运行测试
uv run python tests/test_image_renderer.py
```

## 样式定制

### 修改颜色主题

编辑 `image_renderer.py` 中的 CSS：

```css
body {
    background: #0A0A0A;  /* 背景色 */
    color: #E0E0E0;       /* 文字色 */
}

.title {
    color: #FFFFFF;       /* 标题色 */
}
```

### 调整布局

```css
.images-container {
    gap: 20px;            /* 图片间距 */
}

.image-wrapper img {
    border-radius: 8px;   /* 圆角 */
    border: 1px solid #333; /* 边框 */
}
```

## 技术细节

- **分辨率**: 1080x1440 (3:4 比例)
- **DPI**: 2x (Retina)
- **字体**: SF Mono, Consolas, Monaco
- **图片格式**: PNG (Base64 注入)
- **渲染引擎**: Playwright Chromium

## 常见问题

### Q: 图片显示不全？
A: 检查图片尺寸，建议宽度不超过 960px

### Q: 字体不显示？
A: 确保系统安装了 SF Mono 或 Consolas 字体

### Q: 渲染速度慢？
A: 首次启动 Playwright 会慢，后续会快很多

## 示例输出

生成的卡片会保存到指定路径，例如：
- `test_outputs/card_text_only.png` - 纯文字
- `test_outputs/card_single_image.png` - 单图
- `test_outputs/card_double_image.png` - 双图
