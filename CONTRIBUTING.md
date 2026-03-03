# 贡献指南

感谢你考虑为 Matrix 做出贡献！

## 行为准则

参与本项目即表示你同意遵守我们的行为准则。请保持友善、尊重和包容。

## 如何贡献

### 报告 Bug

如果你发现了 bug，请：

1. 检查 [Issues](https://github.com/iridite/matrix/issues) 确认问题尚未被报告
2. 创建新 Issue，包含：
   - 清晰的标题和描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 环境信息（Python 版本、操作系统等）
   - 相关日志或截图

### 提出新功能

1. 先在 [Discussions](https://github.com/iridite/matrix/discussions) 讨论你的想法
2. 获得反馈后，创建 Feature Request Issue
3. 等待维护者批准后再开始开发

### 提交代码

#### 开发流程

1. **Fork 仓库**
   ```bash
   # 在 GitHub 上 Fork 仓库
   git clone https://github.com/YOUR_USERNAME/matrix.git
   cd matrix
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **安装开发依赖**
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

4. **编写代码**
   - 遵循现有代码风格
   - 添加必要的类型注解
   - 编写清晰的注释
   - 保持函数简洁（单一职责）

5. **运行测试**
   ```bash
   # 运行所有测试
   uv run pytest tests/

   # 代码格式化
   uv run ruff format .

   # Lint 检查
   uv run ruff check .
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

7. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   然后在 GitHub 上创建 Pull Request

#### Commit Message 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）：**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链更新

**示例：**
```
feat(renderer): add support for 3-image layout

- Implement new layout algorithm for 3 images
- Update CSS grid template
- Add tests for 3-image cards

Closes #123
```

### 代码规范

#### Python 风格

- 遵循 [PEP 8](https://pep8.org/)
- 使用 [Ruff](https://github.com/astral-sh/ruff) 进行格式化和 lint
- 最大行长度：100 字符
- 使用类型注解

**示例：**
```python
from typing import Optional

def process_article(
    title: str,
    content: str,
    tags: Optional[list[str]] = None
) -> dict[str, str]:
    """处理文章内容

    Args:
        title: 文章标题
        content: 文章正文
        tags: 可选的标签列表

    Returns:
        处理后的文章字典
    """
    if tags is None:
        tags = []

    return {
        "title": title.strip(),
        "content": content.strip(),
        "tags": tags
    }
```

#### 架构原则

1. **极简主义**：避免过度抽象，优先使用函数而非类
2. **容错性**：单点故障不影响整体流程
3. **可测试性**：编写可测试的纯函数
4. **类型安全**：使用 Pydantic 进行数据验证

### 文档

- 为新功能添加文档到 `docs/` 目录
- 更新 README.md（如果需要）
- 为公共 API 添加 docstring
- 提供使用示例

### 测试

- 为新功能编写测试
- 确保测试覆盖率不降低
- 测试文件命名：`test_*.py`
- 使用 pytest fixtures 复用测试代码

**示例：**
```python
import pytest
from matrix.core.fetcher import fetch_feeds

def test_fetch_feeds_success():
    """测试 RSS 抓取成功场景"""
    feeds = ["https://example.com/feed"]
    articles = fetch_feeds(feeds, max_items_per_feed=5)

    assert len(articles) <= 5
    assert all("title" in a for a in articles)
    assert all("link" in a for a in articles)

def test_fetch_feeds_invalid_url():
    """测试无效 URL 处理"""
    feeds = ["invalid-url"]
    articles = fetch_feeds(feeds)

    assert articles == []  # 应该返回空列表而不是崩溃
```

## Pull Request 流程

1. **PR 标题**：使用 Conventional Commits 格式
2. **描述**：清楚说明改动内容和原因
3. **关联 Issue**：使用 `Closes #123` 或 `Fixes #456`
4. **检查清单**：
   - [ ] 代码通过所有测试
   - [ ] 代码通过 Ruff 检查
   - [ ] 添加了必要的文档
   - [ ] 更新了 CHANGELOG（如果需要）

5. **Code Review**：
   - 维护者会审查你的代码
   - 根据反馈进行修改
   - 保持耐心和友善

6. **合并**：
   - PR 被批准后会被合并到 main 分支
   - 你的贡献会被记录在 Contributors 列表中

## 开发环境设置

### 推荐工具

- **编辑器**：VS Code / PyCharm
- **Python 版本管理**：pyenv
- **包管理器**：uv
- **Git 客户端**：命令行 / GitHub Desktop

### VS Code 配置

创建 `.vscode/settings.json`：

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

## 获取帮助

- 💬 [Discussions](https://github.com/iridite/matrix/discussions) - 提问和讨论
- 🐛 [Issues](https://github.com/iridite/matrix/issues) - Bug 报告和功能请求
- 📧 Email: hello@iridite.dev

## 许可证

提交代码即表示你同意将代码以 MIT License 开源。

---

再次感谢你的贡献！🎉
