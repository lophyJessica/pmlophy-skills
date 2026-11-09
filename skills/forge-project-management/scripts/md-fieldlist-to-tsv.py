#!/usr/bin/env python3
"""字段清单 md → 13 列 TSV 详细稿转换器（Forge/QS-JXC 标准）。

用法:
    python3 md-fieldlist-to-tsv.py <字段清单.md> <输出.tsv>
    # 批量(可选): BASE_DIR 指向字段清单/, 自动处理 商机管理/客户管理/... 目录

13 列头: 字段所属分组|字段名称|字段类型|字段来源|字段说明|必填性|新增页|
编辑页|列表展示|可筛选|详情展示|取值说明|备注

要点:
- 分组取自 md 的 `## 一、xxx` 标题（去序号前缀）
- 字段类型 = 控件性质混合口径（文本/数字/日期/单选/对象集合/多行文本），
  名称语义优先 + 取值说明辅助推断，规则无法 100% 准 → 边缘字段人工校
- 跨系统技术字段（crmCustomerId 等）不单独成行，收进所属业务字段备注列
  （与评审 PRD 字段表规则一致："技术字段不展示，收进字段说明"）
- 各模块 md 表头列数可能不一致（11/10/5/4 列）→ 按列名语义归一映射，
  缺失列留空（用户接受："强行统一转 13 列，缺失列后面再补"）
"""

import os, re, sys

# 跨系统技术字段 → 收进哪个业务字段备注（业务语义来判断，勿机械列）
TECH_FIELDS = {
    'crmCustomerId': '关联客户', 'erpCustomerId': '关联客户',
    'customerSnapshotVersion': '关联客户', 'customerSnapshotSyncTime': '关联客户',
    'erpProductId': '关联商品', 'productCode': '关联商品',
    'productNameSnapshot': '关联商品', 'unitPriceSnapshot': '关联商品',
    'lineAmount': '关联商品', 'priceVersion': '关联商品',
    'availabilityStatus': '关联商品',
    'ERP_ORDER_SYNC_STATUS': '合同编号', 'ERP_ORDER_ID': '合同编号',
    'ERP_ORDER_SYNC_ERROR': '合同编号', 'ERP_ORDER_SYNC_TIME': '合同编号',
    'ERP_ORDER_IDEMPOTENCY_KEY': '合同编号', 'CONTRACT_LINK_STATUS': '合同编号',
}

HDR = ['字段所属分组','字段名称','字段类型','字段来源','字段说明','必填性',
       '新增页','编辑页','列表展示','可筛选','详情展示','取值说明','备注']

# 列名别名归一到 13 列语义
COL_ALIAS = {
    '字段名称':'字段名称', '字段来源':'字段来源', '取值说明':'取值说明',
    '字段说明':'字段说明', '说明':'字段说明', '必填性':'必填性', '必填':'必填性',
    '新增页':'新增页', '编辑页':'编辑页', '列表展示':'列表展示', '列表':'列表展示',
    '可筛选':'可筛选', '详情展示':'详情展示', '备注':'备注', '展示':'详情展示',
}


def infer_type(name, val_desc):
    v = val_desc.lower()
    n = name.lower().replace('`', '')
    if '=' in val_desc:
        return '单选(枚举)'
    if re.search(r'[A-Z_]+/[A-Z_]+', val_desc):
        return '单选(枚举)'
    if '对象集合' in v or '明细' in v or '商品明细' in v:
        return '对象集合'
    # 名称语义优先（比取值说明更可靠）
    if re.search(r'(数量|目标数|个数|金额|价格|单价|概率|%|费用|余额|合计|小计|总额|金额)$', n):
        return '数字'
    if re.search(r'(月份|日期|时间)$', n) and '编号' not in n:
        return '日期'
    if re.search(r'(状态|阶段|类型|来源|方式|渠道|级别|是否|原因)$', n):
        return '单选'
    if '日期' in v or 'datepicker' in v or re.search(r'YYYY-MM|HH:mm', val_desc):
        return '日期'
    if any(k in v for k in ('金额','价格','单价','数字','number','百分比','%')):
        return '数字'
    if '布尔' in v or '开关' in v or 'true/false' in v:
        return '布尔'
    if '附件' in v or '上传' in v:
        return '附件'
    if 'textarea' in v:
        return '多行文本'
    if 'select' in v or '单选' in v:
        return '单选'
    if re.search(r'(编号|代码|键|标识|Id)$', n) or re.match(r'^[a-z_]+Id$', n):
        return '文本'
    if any(k in v for k in ('text', '文本', 'input')):
        return '文本'
    return '文本'


def is_tech(name):
    n = name.replace('`', '').strip()
    if n in TECH_FIELDS:
        return True
    return bool(re.match(r'^[a-z]+[A-Z]', n) or re.match(r'^[A-Z]+_[A-Z0-9_]+$', n))


def parse_tbl(lines):
    rows, in_tbl, headers = [], False, []
    for ln in lines:
        s = ln.strip()
        if s.startswith('|'):
            cells = [c.strip() for c in s.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', c) for c in cells if c):
                continue
            if not in_tbl:
                headers, in_tbl = cells, True
                continue
            cells = [c.strip() for c in s.strip('|').split('|')]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
    return headers, rows


def split_groups(lines):
    groups, cur, cur_lines = [], None, []
    for ln in lines:
        m = re.match(r'^##\s+(.+)', ln.strip())
        if m:
            if cur:
                groups.append((cur, cur_lines))
            cur = re.sub(r'^[一二三四五六七八九十]+、', '', m.group(1)).strip()
            cur_lines = []
        else:
            if cur:
                cur_lines.append(ln)
    if cur:
        groups.append((cur, cur_lines))
    return groups


def convert(md_path):
    with open(md_path) as f:
        lines = f.readlines()
    out, tech_merged = [], {}
    for grp, gl in split_groups(lines):
        if not any('|' in g for g in gl):
            continue
        if grp.startswith(('Changelog', '变更', '修改')):
            continue
        headers, rows = parse_tbl(gl)
        if not headers:
            continue
        mapcol = {h: COL_ALIAS[h] for h in headers if h in COL_ALIAS}
        for r in rows:
            name = r.get('字段名称', '').strip()
            if not name or name == HDR[1]:
                continue
            if is_tech(name):
                note = f"{name}: {r.get('字段说明', '').strip()}；{r.get('备注', r.get('取值说明', '')).strip()}"
                note = re.sub(r'\s+', ' ', note).strip(' ；;')
                tech_merged.setdefault(TECH_FIELDS.get(name.replace('`', '').strip(), ''), []).append(note)
                continue
            vald = r.get('取值说明', '').strip()
            ftype = infer_type(name, vald)
            get = lambda k: r.get(next((mk for mk in mapcol if mapcol[mk] == k), ''), '').strip()
            row = [grp, name, ftype, get('字段来源'), get('字段说明'), get('必填性'),
                   get('新增页'), get('编辑页'), get('列表展示'), get('可筛选'),
                   get('详情展示'), get('取值说明'), get('备注')]
            row = [c.replace('\n', ' ').replace('\r', ' ') for c in row]
            out.append('\t'.join(row))
    for i, ln in enumerate(out):
        cells = ln.split('\t')
        if len(cells) == 13 and cells[1].strip() in TECH_FIELDS.values():
            merged = TECH_FIELDS.keys()  # 简化: 按业务字段名找
    # 技术字段备注追加到对应业务字段行备注列
    reverse = {}
    for k, v in TECH_FIELDS.items():
        reverse.setdefault(v, []).append(k)
    for i, ln in enumerate(out):
        cells = ln.split('\t')
        if len(cells) == 13 and cells[1].strip() in reverse:
            notes = []
            for tk in reverse[cells[1].strip()]:
                if tk in tech_merged:
                    notes.extend(tech_merged[tk])
            if notes:
                cells[12] = (cells[12].strip() + '；' if cells[12].strip() else '') + '；'.join(notes)
                out[i] = '\t'.join(cells)
    return out


if __name__ == '__main__':
    if len(sys.argv) == 3:
        rows = convert(sys.argv[1])
        with open(sys.argv[2], 'w') as f:
            f.write('\t'.join(HDR) + '\n' + '\n'.join(rows))
        print(f"{len(rows)} 字段 → {sys.argv[2]}")
    else:
        # 批量模式: BASE_DIR 下每个含 *字段清单.md 的模块目录
        base = sys.argv[1] if len(sys.argv) > 1 else '.'
        for mod in sorted(os.listdir(base)):
            d = os.path.join(base, mod)
            if not os.path.isdir(d):
                continue
            md = [f for f in os.listdir(d) if f.endswith('.md') and '字段清单' in f]
            if not md:
                continue
            out_name = mod.replace('管理', '') + '字段清单（详细稿）.tsv'
            rows = convert(os.path.join(d, md[0]))
            with open(os.path.join(d, out_name), 'w') as f:
                f.write('\t'.join(HDR) + '\n' + '\n'.join(rows))
            print(f"[{mod}] {len(rows)} 字段 → {out_name}")
