"""笔记源 - 从本地 Markdown 文件读取内容"""
import os
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def fetch_from_notes(notes_dir: str, pattern: str = "*.md") -> List[Dict]:
    """
    从本地 Markdown 笔记读取内容

    Args:
        notes_dir: 笔记目录路径
        pattern: 文件匹配模式（默认 *.md）

    Returns:
        标准化的文章列表，每篇文章包含 source_type="note"
    """
    articles = []
    notes_path = Path(notes_dir)

    if not notes_path.exists():
        print(f"⚠️  笔记目录不存在: {notes_dir}")
        return articles

    # 递归查找所有 Markdown 文件
    for md_file in notes_path.rglob(pattern):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取标题（第一行 # 标题）
            lines = content.split("\n")
            title = lines[0].lstrip("#").strip() if lines else md_file.stem

            # 提取摘要（前 500 字符）
            summary = content[:500].replace("#", "").strip()

            # 构造标准格式
            article = {
                "title": title,
                "link": f"file://{md_file.absolute()}",
                "summary": summary,
                "published_date": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(),
                "source_type": "note",
                "content": content  # 笔记保留完整内容
            }

            articles.append(article)

        except Exception as e:
            print(f"⚠️  读取笔记失败 {md_file}: {e}")
            continue

    print(f"📝 从笔记目录读取 {len(articles)} 篇文章")
    return articles
