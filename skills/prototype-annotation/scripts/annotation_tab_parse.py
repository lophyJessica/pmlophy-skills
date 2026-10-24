"""标注详情六页签解析与条目计数。

与 assets/annotation-kit/runtime.js 中 parseAnnotationTabs、countMarkdownItems 保持同步。
任一侧修改逻辑时，必须同步另一侧（见两文件头部 SYNC 注释）。
"""
from __future__ import annotations

import re
from typing import Dict, List

# SYNC: runtime.js VPA_DETAIL_TABS（不含「全部」）
TAB_LABEL_TO_KEY = {
    "页面内容": "page",
    "交互说明": "interaction",
    "业务规则": "rule",
    "字段说明": "field",
    "待确认": "pending",
}

TAB_KEYS = ("page", "interaction", "rule", "field", "pending")


def parse_annotation_tabs(markdown: str) -> Dict[str, List[str]]:
    sections = {key: [] for key in TAB_KEYS}
    current = None
    for line in str(markdown or "").split("\n"):
        heading = re.match(r"^###\s+(.+)$", line.strip())
        key = TAB_LABEL_TO_KEY.get(heading.group(1).strip()) if heading else None
        if key:
            current = key
            continue
        if current:
            sections[current].append(line)
    return sections


def _is_table_separator(line: str) -> bool:
    cells = str(line or "").strip().split("|")
    if len(cells) <= 2 or cells[0] != "" or cells[-1] != "":
        return False
    return all(re.match(r"^:?-{3,}:?$", cell.strip()) for cell in cells[1:-1])


def count_markdown_items(markdown: str) -> int:
    source = str(markdown or "")
    lines = source.split("\n")
    list_items = 0
    table_rows = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*(?:[-+*]|\d+[.)、])\s+", line):
            list_items += 1
        elif re.match(r"^\s*\|", line) and not _is_table_separator(line):
            if i + 1 < len(lines) and _is_table_separator(lines[i + 1]):
                i += 1
            else:
                table_rows += 1
        i += 1
    return list_items + table_rows


def tab_body(sections: Dict[str, List[str]], key: str) -> str:
    return "\n".join(sections.get(key, [])).strip()


def is_empty_tab_body(body: str) -> bool:
    text = re.sub(r"\s+", "", body or "")
    if not text:
        return True
    return text in ("暂无", "暂无。")
