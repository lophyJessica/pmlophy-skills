#!/usr/bin/env python3
"""评审PRD变更回写：对比评审PRD vs 权威源，输出分层待回写清单。
核心是"主动找变更"：解析评审PRD的字段表/规则表，和权威源(字段清单.md / 主PRD.md)对应内容做差异对比，
以评审PRD为主，列出"权威源需要回写对齐"的项。为避免把"表述不同"误判成本质差异，分三层输出：

  ① 确定差异(必回写)   —— 权威源真缺该字段/规则，或必填性真变了
  ② 需人工确认         —— 疑似同字段不同名 / 来源与说明详细度不同 / 规则措辞不同(语义可能一致)
  ③ 一致               —— 无需回写

用法:
  python3 diff_backfill.py --review-prd <评审PRD.md> --field-src <字段清单.md> --main-prd <主PRD.md>
  --only-diff  只输出 ① + ② (待回写清单)；--confirm-only 只输出 ② (给人确认)
  --table      输出 md 表格格式(可直接当待回写清单.md)
"""
import argparse, re, sys


def parse_md_tables(text):
    lines = text.split("\n")
    tables = []
    cur_heading = ""
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("#"):
            cur_heading = ln.lstrip("#").strip()
        if "|" in ln and i + 1 < len(lines) and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in ln.strip(" |").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip() != "":
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(cells) >= len(header):
                    rows.append(dict(zip(header, cells)))
                i += 1
            tables.append({"heading": cur_heading, "header": header, "rows": rows})
            continue
        i += 1
    return tables


def collect_fields(tables, is_review):
    """从表格列表收集字段: [{name, required, source, hint, heading}]。
    is_review=True 时按评审PRD规则(6.x heading + 字段名称表头)，否则按权威源(含字段名称表头均可)。"""
    out = []
    for t in tables:
        hdr = t["header"]
        if "字段名称" not in hdr:
            continue
        heading = t["heading"] or ""
        # 评审PRD字段表 heading 形如 "6.1 商机列表页"；权威源字段清单 heading 形如 "一、基础信息字段"
        if not heading.startswith(("6.", "五", "一", "二", "三", "四")):
            continue
        for row in t["rows"]:
            name = row.get("字段名称", "").strip()
            if not name or name.startswith("|"):
                continue
            out.append({
                "name": name,
                "required": row.get("是否必填", row.get("必填性", "")).strip(),
                "source": row.get("字段来源", "").strip(),
                "hint": row.get("字段说明", "").strip(),
                "heading": heading,
            })
    return out


def collect_rules(tables):
    """收集业务规则: 评审PRD(5.x heading)返回 [{cond,res,heading}]。"""
    out = []
    for t in tables:
        hdr = t["header"]
        if "什么情况下" in hdr and "结果" in hdr and re.match(r"^5\.\d+", (t["heading"] or "")):
            for row in t["rows"]:
                cond = row.get("什么情况下", "").strip()
                res = row.get("结果", "").strip()
                if cond:
                    out.append({"cond": cond, "res": res, "heading": t["heading"]})
    return out


def norm(s):
    return re.sub(r"[，。；、\s\"']", "", s or "")


# 评审PRD字段名 与 权威源字段名 的别名映射(评审PRD对同一字段可能用不同叫法, 尤其是列表页)
FIELD_ALIAS = {
    "客户名称": "关联客户",
    "AI成交概率": "AI成交概率",
    "商品明细": "关联商品",
    "当前阶段": "商机阶段",
}


def canonical_name(name):
    return FIELD_ALIAS.get(name, name)


# 必填性归一：不同系统对"自动"的写法多种
def norm_required(s):
    s = norm(s)
    if s in ("系统自动", "系统生成", "只读"):  # 非用户填写纬度
        return "auto"
    if "必填" in s:
        return "required" if s in ("必填", "是") else "cond_required"
    if s in ("选填", "否", ""):
        return "optional"
    return s


def source_consistent(rev, auth):
    """评审PRD来源 与 权威源来源 是否"语义一致"(权威源通常更详细, 评审PRD是摘要)。
    只要评审PRD的来源短语被权威源包含(或互为子串), 视为一致。"""
    r, a = norm(rev), norm(auth)
    if not r or not a:
        return True
    if r == a:
        return True
    # 权威源更详细: "用户选择,数据来源为CRM客户快照..." 包含 "用户选择"
    if r in a or a in r:
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review-prd", required=True)
    ap.add_argument("--field-src", required=True)
    ap.add_argument("--main-prd", required=True)
    ap.add_argument("--only-diff", action="store_true", help="只输出①+②")
    ap.add_argument("--confirm-only", action="store_true", help="只输出②需人工确认")
    ap.add_argument("--table", action="store_true", help="输出md表格")
    a = ap.parse_args()

    rp = open(a.review_prd, encoding="utf-8").read()
    fs = open(a.field_src, encoding="utf-8").read()
    mp = open(a.main_prd, encoding="utf-8").read()

    rp_tables = parse_md_tables(rp)
    fs_tables = parse_md_tables(fs)
    mp_tables = parse_md_tables(mp)

    diffs = []      # ① 确定差异
    confirms = []   # ② 需人工确认

    # ===== 字段对比(去重三页同名) =====
    rp_fields = collect_fields(rp_tables, is_review=True)
    fs_fields = collect_fields(fs_tables, is_review=False)
    fs_index = {canonical_name(f["name"]): f for f in fs_fields}

    # 评审PRD字段去重(同名取一, 合并来源页)
    seen = {}
    for ff in rp_fields:
        key = canonical_name(ff["name"])
        if key not in seen:
            seen[key] = ff
        else:
            # 合并说明(跨页不同说明时保留首个完整)
            if not seen[key]["hint"] and ff["hint"]:
                seen[key]["hint"] = ff["hint"]
    rp_unique = list(seen.values())

    for ff in rp_unique:
        cname = canonical_name(ff["name"])
        fs_f = fs_index.get(cname)
        if fs_f is None:
            diffs.append(("字段", f"字段「{ff['name']}」在字段清单缺失(评审PRD有, 权威源无)", a.field_src))
            continue
        # 必填差异: 追名归一后仍不同才算
        r_req = norm_required(ff["required"])
        a_req = norm_required(fs_f["required"])
        req_diff = r_req != a_req and not (r_req == "cond_required" and a_req in ("required", "cond_required"))
        # 来源差异: 语义降噪
        src_diff = not source_consistent(ff["source"], fs_f["source"])
        if req_diff:
            diffs.append(("字段", f"字段「{ff['name']}」必填性不同: 评审PRD={ff['required']} 字段清单={fs_f['required']}", a.field_src))
        elif src_diff:
            confirms.append(("字段", f"字段「{ff['name']}」来源表述待确认: 评审PRD={ff['source']} 字段清单={fs_f['source']}", a.field_src))
        # 如果 required 也命名不同但算一致 → 不报

    # ===== 规则对比(弱化: 只报权威源完全无此语义) =====
    rp_rules = collect_rules(rp_tables)
    # 主PRD规则文本(拼接 + 每条的规范化)
    main_rule_texts = []
    for t in mp_tables:
        if "规则ID" in t["header"] or "rule" in "".join(t["header"]).lower():
            for row in t["rows"]:
                rule = row.get("规则", "") or row.get("规则内容", "") or ""
                if rule:
                    main_rule_texts.append(norm(rule))
    main_rule_blob = "".join(main_rule_texts)

    for r in rp_rules:
        key = norm(r["cond"])
        in_main = key and (
            key in main_rule_blob or
            any(key in t for t in main_rule_texts)
        )
        if not in_main:
            # 弱化: 标"需人工确认"——评审PRD有这条, 主PRD规则未直接匹配(可能措辞不同或真新增)
            confirms.append(("规则", f"[{r['heading']}] 条件「{r['cond']}」在主PRD规则中未直接匹配(评审PRD新增/表述不同, 人工核对)", a.main_prd))

    # ===== 输出 =====
    if a.only_diff:
        rows = [("①确定", typ, desc, target) for (typ, desc, target) in diffs] + \
               [("②确认", typ, desc, target) for (typ, desc, target) in confirms]
        if a.table:
            print("| 分级 | 类型 | 改动摘要 | 回写目标 |")
            print("|------|------|---------|---------|")
            for lvl, typ, desc, target in rows:
                desc = desc.replace("|", "/")
                print(f"| {lvl} | {typ} | {desc} | {target} |")
        else:
            for lvl, typ, desc, target in rows:
                print(f"{lvl}\t{typ}\t{desc}\t{target}")
        return 0

    if a.confirm_only:
        for (typ, desc, target) in confirms:
            print(f"{typ}\t{desc}\t{target}")
        return 0

    # 默认: 三段全量
    print("=== ①确定差异(必回写) ===")
    if diffs:
        for typ, desc, target in diffs:
            print(f"  [{typ}] {desc}  -> {target}")
    else:
        print("  (无)")
    print("\n=== ②需人工确认(语义可能一致, 核对后决定) ===")
    if confirms:
        for typ, desc, target in confirms:
            print(f"  [{typ}] {desc}  -> {target}")
    else:
        print("  (无)")
    print(f"\n差异总量: 确定 {len(diffs)} 项 + 需确认 {len(confirms)} 项")
    return 0


if __name__ == "__main__":
    sys.exit(main())