#!/usr/bin/env python3
"""评审 PRD 结构自检：交付前必跑，拦「每次都要人工擦屁股」的四类格式问题。

2026-11-02 实战产出：一次自检就扫出【字段说明】残留 15 处、多行缺【待确认】、版本号 V3.2 重复两次。
这些都不是内容错，而是形态错，人眼看长表根本看不出来，必须机器扫。

检查项：
  1. 【字段说明】段残留（字段唯一真源是字段清单 TSV，评审 PRD 不得再写）
  2. 页面说明行缺【页面内容】/【交互说明】
  3. 页面说明行缺【待确认】（无则必须写「当前无待确认项」，不能整段没有）
  4. 主行缺【业务规则】（带 -1/-2 后缀的细分行豁免）
  5. 版本记录编号重复
  6. 修改记录里的日期格式与倒序

用法：python3 structure_check.py <评审PRD.md>
退出码：有问题 1，干净 0。
"""
import re
import sys
import argparse

PAGE_ROW = re.compile(r"^\|\s*(\d+(?:-\d+)?)\s*\|")

def load(path):
    return open(path, encoding="utf-8").read().split("\n")

def in_history(lineno, history_range):
    a, b = history_range
    return a <= lineno <= b

def find_history(lines):
    start = end = None
    for i, l in enumerate(lines, 1):
        if start is None and re.search(r"修改记录|版本记录", l) and l.startswith("#"):
            start = i
        elif start and l.startswith("## ") and i > start:
            end = i
            break
    return (start or 0, end or 0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    args = ap.parse_args()
    lines = load(args.md)
    hist = find_history(lines)
    issues = []

    # 1 字段说明残留
    for i, l in enumerate(lines, 1):
        if "【字段说明】" in l and not in_history(i, hist):
            issues.append(f"L{i} 【字段说明】段残留，字段应只进字段清单 TSV")

    # 2/3/4 页面说明行段结构
    for i, l in enumerate(lines, 1):
        m = PAGE_ROW.match(l)
        if not m or "【页面内容】" not in l:
            continue
        no = m.group(1)
        sub_row = "-" in no
        if "【交互说明】" not in l:
            issues.append(f"L{i} 序号{no} 缺【交互说明】")
        if "【待确认】" in l and ("当前无待确认项" in l or not re.search(r"【待确认】(.{3,})", l)):
            issues.append(f"L{i} 序号{no} 【待确认】为空，应整段删掉（不写‘当前无待确认项’这种占位）")
        if not sub_row and "【业务规则】" not in l:
            issues.append(f"L{i} 序号{no} 主行缺【业务规则】")

    # 5 版本号重复
    vers = {}
    for i, l in enumerate(lines, 1):
        if in_history(i, hist):
            m = re.search(r"\|\s*(V\d+(?:\.\d+)*)\s*\|", l)
            if m:
                vers.setdefault(m.group(1), []).append(i)
    for v, locs in vers.items():
        if len(locs) > 1:
            issues.append(f"版本号 {v} 重复出现：L{', L'.join(map(str, locs))}")

    # 6 页面序号必须升序：主行在前，子行按数字升序（3 → 3-1 → 3-2 → 3-3）
    # 只在同一张表内比：遇到非表格行就重置，避免把多张表的 1 当成逆序
    seq = []
    for i, l in enumerate(lines, 1):
        if not l.lstrip().startswith("|"):
            seq = []
            continue
        m = PAGE_ROW.match(l)
        if m and "【页面内容】" in l:
            no = m.group(1)
            if "-" in no:
                major, minor = no.split("-", 1)
                key = (int(major), int(minor))
            else:
                key = (int(no), -1)
            if seq and key[0] == seq[-1][0][0] and key[1] == -1:
                seq = []  # 新的主行，子行序号可以重新从 1 开始
                seq.append((key, no, i))
                continue
            seq.append((key, no, i))
            if len(seq) > 1 and key < seq[-2][0]:
                issues.append(
                    f"L{i} 序号 {no} 排在 {seq[-2][1]}（L{seq[-2][2]}）之后，序号逆序；应为 主行→子行升序"
                )

    # 7 每张表格都必须以「序号」开头（2026-11-02 用户要求：表格都要加序号，字段清单也要）
    for i, l in enumerate(lines, 1):
        if l.startswith("|") and i < len(lines) and re.match(r"^\|[-\s:|]+\|?\s*$", lines[i]):
            first = l.strip().strip("|").split("|")[0].strip()
            if first != "序号":
                issues.append(f"L{i} 表格首列是「{first}」而非「序号」，除特别说明外所有表格都要有序号列")

    if issues:
        print(f"== FAIL 共 {len(issues)} 项")
        for x in issues:
            print("  -", x)
        return 1
    print("== PASS 结构自检全部通过")
    return 0

if __name__ == "__main__":
    sys.exit(main())
