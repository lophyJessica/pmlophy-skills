#!/usr/bin/env python3
"""核验 agent 交回来的功能清单 TSV：列完整性 + 代码依据真伪 + 粒度 + 重复。

用法: python3 verify_feature_tsv.py <清单.tsv> <源码根目录>
退出码 0 = 全过；1 = 有问题。
"""
import csv, os, re, sys
from collections import Counter

EXPECT_COLS = 9


def main():
    if len(sys.argv) < 3:
        print("用法: verify_feature_tsv.py <清单.tsv> <源码根目录>")
        return 2
    fpath, root = sys.argv[1], sys.argv[2]
    rows = list(csv.reader(open(fpath, encoding="utf-8"), delimiter="\t"))
    if not rows:
        print("[FAIL] 空文件")
        return 1
    hdr = rows[0]
    data = [r for r in rows[1:] if len(r) >= EXPECT_COLS and r[0].strip() and r[1].strip()]
    fails, warns = [], []

    print("== 1 结构")
    print(f"  表头 {len(hdr)} 列：{hdr[:3]}...")
    if len(hdr) != EXPECT_COLS:
        fails.append(f"表头列数 {len(hdr)} ≠ {EXPECT_COLS}")
    print(f"  数据行：{len(data)}")

    print("== 2 列填充")
    support = Counter(r[5].strip() for r in data)
    conf = Counter(r[6].strip() for r in data)
    blank_shot = sum(1 for r in data if not r[4].strip())
    blank_export = sum(1 for r in data if not r[7].strip() and not r[8].strip())
    print(f"  是否支持：{dict(support)}")
    print(f"  内容可配：{dict(conf)}")
    print(f"  截图为空 {blank_shot}/{len(data)}，外销两列为空 {blank_export}/{len(data)}")
    if set(support) - {"√"}:
        warns.append("是否支持列出现非 √ 值，确认是否符合内销基准口径")

    print("== 3 代码依据真伪")
    ok = miss = bad = 0
    bad_samples = []
    for r in data:
        for m in re.finditer(r"([\w\-./]+\.(?:vue|js|ts|tsx|jsx)):(\d+)", r[3]):
            path, ln = m.group(1), int(m.group(2))
            full = os.path.join(root, path)
            if not os.path.isfile(full):
                miss += 1
                if len(bad_samples) < 5:
                    bad_samples.append(("缺文件", path, r[3][:60]))
                continue
            n = sum(1 for _ in open(full, encoding="utf-8", errors="replace"))
            if ln > n:
                bad += 1
                if len(bad_samples) < 5:
                    bad_samples.append((f"行号越界 {ln}>{n}", path, r[3][:60]))
            else:
                ok += 1
    print(f"  有效 {ok} / 缺文件 {miss} / 行号越界 {bad}")
    for s in bad_samples:
        print("   ", s)
    if miss or bad:
        fails.append(f"代码依据有问题：缺文件 {miss}、行号越界 {bad}")

    print("== 4 粒度与重复")
    pages = Counter(r[0].strip() for r in data)
    print("  页面数：", len(pages))
    thin = [(p, c) for p, c in pages.items() if c < 5]
    thick = [(p, c) for p, c in pages.items() if c > 30]
    if thin:
        warns.append(f"{len(thin)} 个页面不足 5 行（容器页可接受）：{thin[:5]}")
    if thick:
        warns.append(f"{len(thick)} 个页面超过 30 行，可能过拆：{thick[:5]}")
    dup = [(k, v) for k, v in Counter((r[0].strip(), r[1].strip()) for r in data).items() if v > 1]
    print("  重复子功能项：", len(dup), dup[:3])

    print("== 汇总")
    for w in warns:
        print("  [WARN]", w)
    for f in fails:
        print("  [FAIL]", f)
    print("  结论:", "通过" if not fails else "不通过")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
