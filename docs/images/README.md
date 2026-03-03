# 图片资源

## 需要添加的图片

1. **wechat_qr.png** - 微信群二维码（200x200）
2. **card_text_only.png** - 纯文字卡片示例
3. **card_with_image.png** - 图文卡片示例

## 生成示例卡片

运行以下命令生成示例卡片：

```bash
uv run python tests/test_image_renderer.py
```

然后将生成的卡片复制到此目录：

```bash
cp test_outputs/card_text_only.png docs/images/
cp test_outputs/card_single_image.png docs/images/card_with_image.png
```
