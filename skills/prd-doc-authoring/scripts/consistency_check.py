#!/usr/bin/env python3
"""评审 PRD 数字口径清单提取（辅助人工比对，不做自动判定）。

为什么不是自动判冲突：2026-11-02 实测两次失败。
  1）按「名词+量词」聚类会把「行为名称限 20 字」与「行为描述限 500 字」误报成冲突；
  2）改成按子句模板聚类后，真正的错（行为块「最多 4 组」vs「最多 5 条」）反而掳不到——
     两处量词不同（组/条），模板不同，自动聚类天生看不见语义相同的不同量词。
结论：这类检查靠人，脚本只负责把全文的数字口径一口气摆到一屏里，省掉翻全文的力气。

用法：
    python3 consistency_check.py <源稿.md> [--proto <原型src目录>]

输出：
  1. 全文「数字+量词」清单（按量词分组，带行号与子句上下文），供按主题人工比对；
  2. 给 --proto 时，并列原型代码里的硬上限（MAX_*、maxLength、slice(0,N)）供逐项对。
只读，不改文件，退出码始终 0（判定交给人）。
"""
import re
import sys
import os
import glob
import argparse

UNITS = "组|条|位|字|个|项|列|行|次|天|台|秒|分钟"
PAT = re.compile(r"(\d{1,4})\s*(" + UNITS + r")")
# 交付前必看的人工核对主题（写进输出提醒，不参与自动判定）
TOPICS = [
    "追加/上限：X 组 与 X 条 是不是同一件事（量词不同但语义相同时最容易错）",
    "字符长度：名称/描述/ID 各位数",
    "列表列数、展示列数、导出列数是否一致",
    "筛选个数、页签个数、步骤个数",
    "轮询/超时/保存时长等时间数字",
]


def clause(line: str, pos: int) -> str:
    seps = ["，", "。", "；", "|", "<br>"]
    left = max(line.rfind(s, 0, pos) for s in seps)
    right_candidates = [line.find(s, pos) for s in seps if line.find(s, pos) != -1]
    right = min(right_candidates) if right_candidates else len(line)
    return line[left + 1: right].strip()[:70]


def scan_md(path: str):
    by_unit = {}
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            for m in PAT.finditer(line):
                num, unit = m.group(1), m.group(2)
                by_unit.setdefault(unit, []).append((num, lineno, clause(line, m.start())))
    return by_unit


def scan_proto(root: str):
    pats = [
        ("MAX_\w+\s*=\s*(\d+)", "常量上限"),
        (r"maxLength=\{(\d+)\}", "输入长度"),
        (r"\.slice\(0,\s*(\d+)\)", "切片个数"),
    ]
    out = []
    files = glob.glob(os.path.join(root, "**", "*.tsx"), recursive=True) + glob.glob(
        os.path.join(root, "**", "*.ts"), recursive=True
    )
    for f in files:
        try:
            txt = open(f, encoding="utf-8").read()
        except Exception:
            continue
        for pat, kind in pats:
            for m in re.finditer(pat, txt):
                line = txt[: m.start()].count("\n") + 1
                out.append((kind, m.group(1), os.path.basename(f), line))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--proto")
    args = ap.parse_args()

    by_unit = scan_md(args.md)
    print("== 1 全文数字口径清单（按量词分）")
    for unit in sorted(by_unit, key=lambda u: -len(by_unit[u])):
        rows = by_unit[unit]
        uniq = sorted({n for n, _, _ in rows}, key=lambda x: int(x))
        print(f"\n  【{unit}】共 {len(rows)} 处，取值有: {', '.join(uniq)}")
        for num, lineno, ctx in rows:
            print(f"    {num}{unit} @L{lineno}  …{ctx}")

    print("\n== 2 人工核对必看主题")
    for i, t in enumerate(TOPICS, 1):
        print(f"  {i}. {t}")

    if args.proto:
        print("\n== 3 原型代码硬上限（逐项对上面的清单）")
        for kind, num, fname, line in scan_proto(args.proto):
            print(f"  {kind:8s} {num:>5s}  {fname}:{line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
