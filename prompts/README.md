# Prompts 目录

这个目录存放所有 AI 模型的提示词模板，便于统一管理和调优。

## 文件说明

### `sniper_system.txt`
- **用途**: AI 过滤器的系统提示词
- **模型**: Claude 3.5 Haiku
- **任务**: 判断文章是否值得深度改写
- **变量**: `{title}`, `{summary}`, `{link}`

### `writer_system.txt`
- **用途**: AI 内容生成器的系统提示词
- **模型**: Claude 3.5 Sonnet
- **任务**: 生成降维打击式的深度文章
- **变量**: `{suggested_angle}`, `{article_summary}`

## 调优建议

### 过滤准则调整
编辑 `sniper_system.txt` 中的"过滤准则"部分，可以调整：
- 通过/拒绝的内容类型
- 判断标准的严格程度
- 输出的分类维度

### 写作风格调整
编辑 `writer_system.txt` 中的"创作纪律"部分，可以调整：
- 语言风格（极简 vs 详细）
- 态度倾向（冷酷 vs 温和）
- 结尾方式（代码建议 vs 总结升华）

## 使用方式

模块会自动从这个目录加载对应的 prompt 文件：

```python
# sniper.py
prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "sniper_system.txt")
with open(prompt_path, "r", encoding="utf-8") as f:
    template = f.read()
```

修改 prompt 文件后，无需重启程序，下次运行时会自动加载新版本。

## 版本控制

所有 prompt 文件都纳入 git 版本控制，方便：
- 追踪提示词的演化历史
- 回滚到之前的版本
- 团队协作时同步提示词
