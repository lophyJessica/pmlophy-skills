#!/usr/bin/env python3
"""评审 PRD 一键交付：旧口径扫描 + 图引用核对 + 重生成发布版 + 三项自检。

用法:
    python3 deliver.py <评审PRD源稿.md> [--output 发布版.md] [--prev 上一版发布版.md]
                       [--keywords 关键词文件] [--images-dir images] [--allow-drop 15]

退出码: 0 全过；1 有 FAIL（阻断发布）。

约定:
- 只扫源稿，不扫 *-发布版*.md（发布版内嵌 base64，一行几万字符，扫了会把输出打爆）。
- 关键词命中若落在「修改记录」章节内，视为历史记录，计 WARN 不阻断。
- 关键词表优先 --keywords 指定文件，其次源稿同目录 .prd-legacy-terms.txt，
  最后回退到本 skill 内置 references/legacy-terms.txt。一行一个词，# 起注释。
"""
import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_TERMS = os.path.join(HERE, "..", "references", "legacy-terms.txt")
IMG_REF = re.compile(r"!\[[^\]]*\]\(\s*\.?/?([^)\s]+\.(?:png|jpg|jpeg|gif|webp))", re.I)
VERSION_LOG = re.compile(r"^#{1,6}\s*.*修改记录")


def load_terms(path_arg, md_path):
    candidates = []
    if path_arg:
        candidates.append(path_arg)
    candidates.append(os.path.join(os.path.dirname(os.path.abspath(md_path)), ".prd-legacy-terms.txt"))
    candidates.append(SKILL_TERMS)
    for path in candidates:
        if path and os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                terms = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
            return path, terms
    return None, []


def version_log_range(lines):
    """返回 修改记录 章节的行号区间（1-based，含端点）。

    修改记录在文档顶部（版本行正下方），所以不能「从该标题到文末都算历史」——
    那样正文全被豁免，注入旧口径也检不出来。区间到下一个标题行为止。
    """
    start = None
    for i, ln in enumerate(lines, 1):
        if VERSION_LOG.match(ln):
            start = i
            break
    if start is None:
        return 0, 0
    end = len(lines)
    for j in range(start, len(lines)):
        if re.match(r"^#{1,6}\s", lines[j]):
            end = j
            break
    return start, end


IMG_INLINE = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def scan_terms(md_path, terms):
    """扫描旧口径。

    分两档：正文命中 = FAIL（阻断发布）；只出现在图片引用/文件名里的命中 = WARN
    （图名带旧词属清理清单，按用户门禁分层不卡发布，但必须报出来）。
    """
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    lo, hi = version_log_range(lines)
    hits, history, name_only = [], [], []
    for i, ln in enumerate(lines, 1):
        for t in terms:
            if not t or t not in ln:
                continue
            if lo <= i <= hi:
                history.append((i, t, ln.strip()[:120]))
            elif t in IMG_INLINE.sub("", ln):
                hits.append((i, t, ln.strip()[:120]))
            else:
                name_only.append((i, t, ln.strip()[:120]))
    return hits, history, name_only


def check_images(md_path, images_dir):
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    refs = [m.group(1) for m in IMG_REF.finditer(text)]
    base = os.path.dirname(os.path.abspath(md_path))
    missing = [r for r in refs if not os.path.isfile(os.path.join(base, r))]
    idir = os.path.join(base, images_dir)
    on_disk = []
    if os.path.isdir(idir):
        for name in sorted(os.listdir(idir)):
            if name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                on_disk.append(f"{images_dir}/{name}")
    unused = [p for p in on_disk if p not in refs]
    return refs, missing, unused


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--output")
    ap.add_argument("--prev")
    ap.add_argument("--keywords")
    ap.add_argument("--images-dir", default="images")
    ap.add_argument("--allow-drop", type=float, default=10.0,
                    help="发布版比上一版缩小超过该百分比则 FAIL（默认 10）")
    a = ap.parse_args()

    md = os.path.abspath(a.md)
    if not os.path.isfile(md):
        print(f"[FAIL] 源稿不存在: {md}")
        return 1
    if "发布版" in os.path.basename(md):
        print("[FAIL] 传入的是发布版，deliver.py 只接受源稿（发布版由脚本自己生成）")
        return 1

    stem = os.path.splitext(md)[0]
    out = os.path.abspath(a.output) if a.output else stem + "-发布版.md"
    prev = a.prev
    if prev is None and os.path.isfile(out):
        prev = out

    fails, warns = [], []

    # 1 旧口径扫描
    terms_file, terms = load_terms(a.keywords, md)
    hits, history, name_only = scan_terms(md, terms)
    print(f"== 1 旧口径扫描（关键词 {len(terms)} 条，来源 {terms_file or '无'}）")
    for line_no, term, text in hits:
        print(f"  [命中] L{line_no} 「{term}」 {text}")
    for line_no, term, text in name_only:
        print(f"  [仅图名] L{line_no} 「{term}」 {text}")
    for line_no, term, text in history:
        print(f"  [历史] L{line_no} 「{term}」 {text}（修改记录内，不计阻断）")
    if hits:
        fails.append(f"旧口径正文命中 {len(hits)} 处")
        print(f"  结果: FAIL 正文命中 {len(hits)} 处")
    else:
        print(f"  结果: PASS 正文 0 处（仅图名 {len(name_only)} 处转清理清单，"
              f"修改记录内 {len(history)} 处不计）")
    if name_only:
        warns.append(f"图名/引用带旧词 {len(name_only)} 处，需改名并连带改引用")

    # 2 图引用核对
    refs, missing, unused = check_images(md, a.images_dir)
    print(f"== 2 图引用核对（引用 {len(refs)} 张）")
    for m in missing:
        print(f"  [缺失] {m}")
    for u in unused:
        print(f"  [未引用] {u}")
    if missing:
        fails.append(f"图引用缺文件 {len(missing)} 张")
        print(f"  结果: FAIL 缺 {len(missing)} 张")
    else:
        print(f"  结果: PASS 引用全部有文件" + (f"；{len(unused)} 张未被引用（WARN）" if unused else ""))
        if unused:
            warns.append(f"images 目录有 {len(unused)} 张未被引用")

    # 3 重生成发布版
    print(f"== 3 重生成发布版 → {out}")
    embed = os.path.join(HERE, "embed_images.py")
    r = subprocess.run([sys.executable, embed, md, "--output", out], capture_output=True, text=True)
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0:
        fails.append("embed_images 失败")
        print("  结果: FAIL 重生成失败")
        return report(fails, warns)

    # 4 三项自检
    with open(out, encoding="utf-8") as f:
        pub = f.read()
    n_base64 = pub.count("base64,")
    residue = pub.count("images/")
    size = os.path.getsize(out)
    print("== 4 三项自检")
    ok1 = n_base64 == len(refs)
    print(f"  ① base64 图数 {n_base64} vs 引用 {len(refs)} → {'PASS' if ok1 else 'FAIL'}")
    if not ok1:
        fails.append(f"base64 图数 {n_base64} ≠ 引用数 {len(refs)}")
    ok2 = residue == 0
    print(f"  ② 相对路径残留 {residue} → {'PASS' if ok2 else 'FAIL'}")
    if not ok2:
        fails.append(f"发布版残留 images/ 相对路径 {residue} 处")
    if prev and os.path.isfile(prev) and os.path.abspath(prev) != out:
        drop = (os.path.getsize(prev) - size) / os.path.getsize(prev) * 100
        ok3 = drop <= a.allow_drop
        print(f"  ③ 字节数 {size // 1024} KB vs 上一版 {os.path.getsize(prev) // 1024} KB，变化 {drop:+.1f}% → "
              f"{'PASS' if ok3 else 'FAIL'}（阈值 ≤{a.allow_drop}% 缩小）")
        if not ok3:
            fails.append(f"发布版比上一版缩小 {drop:.1f}%，疑似图片丢失")
    else:
        print(f"  ③ 字节数 {size // 1024} KB（无上一版可比，跳过）")

    return report(fails, warns)


def report(fails, warns):
    print("== 汇总")
    for w in warns:
        print(f"  [WARN] {w}")
    if fails:
        for f in fails:
            print(f"  [FAIL] {f}")
        print("  结论: 不可发布")
        return 1
    print("  结论: 全部通过，可发布")
    return 0


if __name__ == "__main__":
    sys.exit(main())
