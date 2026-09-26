#!/usr/bin/env python3
"""从原型标注文件(annotations/pages/*.md)自动提取"页面说明"内容，供给评审PRD的页面和操作表。
标注块结构: <!-- anno:start id=N type=... target=锚点 -->  ## 需求描述：【名称】 ... <!-- anno:end id=N -->
本脚本把每块的正文提取成评审PRD页面说明文本。**只保留"页面内容/交互说明/业务规则"的连贯说明**，
剔除: 来源引用行、表格行(字段另有字段清单表)、"待确认"段落(是评审记录不是页面说明)、标注结构标题。
用法:
  python3 extract_body.py annotations/pages/opportunities-list.md > 说明.txt
多页: python3 extract_body.py <三个页md>...
"""
import re, sys, os


def parse_blocks(md_text):
    block_re = re.compile(
        r'<!--\s*anno:start\s+id=(\d+)\s+type=(\w+)\s+(?:page=([^\s]+)\s+)?target=([^\s>]+)\s*-->(.*?)<!--\s*anno:end\s+id=\1\s*-->',
        re.S)
    out = []
    for m in block_re.finditer(md_text):
        aid, atype, page, target = m.group(1), m.group(2), m.group(3), m.group(4)
        body = m.group(5)
        tm = re.search(r'##\s*需求描述：\s*【([^】]+)】', body)
        title = tm.group(1) if tm else ""
        lines = []
        in_confirm = False
        for ln in body.split("\n"):
            ln = ln.strip()
            if not ln:
                continue
            # 进入"待确认"就跳过该块后面全部内容(它是评审记录,不是页面说明)
            if "待确认" in ln:
                in_confirm = True
                continue
            if in_confirm:
                continue
            # 统计当前在哪个小节 — 我们要的正文来自 页面内容/交互说明/业务规则
            # 表格行(| 隔开) 剔除
            if ln.startswith("|"):
                continue
            # 来源引用/需求标题/结构注释/小节标题 剔除
            if ln.startswith("> 来源") or ln.startswith("## ") or ln.startswith(">"):
                continue
            if ln.startswith("<"):
                continue
            if ln.startswith("####") or ln.startswith("###"):
                continue
            if ln.startswith("- "):
                ln = ln[2:]
            ln = re.sub(r'`([^`]*)`', r'\1', ln)
            ln = ln.replace("**", "")
            if ln and not ln.startswith("|"):
                lines.append(ln)
        out.append({"id": aid, "type": atype, "target": target, "title": title,
                    "text": "；".join(lines).strip("；")})
    return out


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    for path in argv:
        with open(path, encoding="utf-8") as f:
            md = f.read()
        blocks = parse_blocks(md)
        print(f"# {os.path.basename(path)} ({len(blocks)} 块)")
        for b in blocks:
            print(f"\n[{b['id']}] {b['title']}")
            print(b["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))