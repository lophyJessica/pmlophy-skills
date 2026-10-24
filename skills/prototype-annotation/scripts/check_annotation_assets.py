#!/usr/bin/env python3
"""Check deployable prototype annotation assets.

No network or third-party dependencies. Validates the compiled annotation-kit dir:
bundle completeness, anchors, routes, screen-state id rules, and Markdown tab shape.

可选参数：

    --src         前端源码目录（判据 1）
    --routes      路由文件（判据 2）
    --config      annotation.config.json（判据 9、10）
    --prd-pages   本 PRD 页面清单，逗号或换行分隔（判据 10）

判据 11：scopeLabel 以「弹窗」「抽屉」「弹层」开头时不得使用 host（或未填）screenState。

六页签解析与 runtime.js 共用 scripts/annotation_tab_parse.py（与 runtime 内函数同步）。
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from annotation_tab_parse import (
    TAB_KEYS,
    count_markdown_items,
    is_empty_tab_body,
    parse_annotation_tabs,
    tab_body,
)

SOURCE_SUFFIXES = {'.tsx', '.ts', '.jsx', '.js', '.vue', '.html'}

FIELD_TABLE_HEADER = re.compile(
    r"字段名称\s*\|\s*是否必填\s*\|\s*是否可编辑\s*\|\s*约束与校验"
)
POINTER_PHRASE = re.compile(r"见\s*§|参见")
DISPLAY_SOURCE = re.compile(r"(?:^|\n)\s*(?:>\s*)?来源\s*[:：]", re.MULTILINE)


def collect_source_text(src: Path) -> str:
    chunks = []
    for path in sorted(src.rglob('*')):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if 'node_modules' in path.parts or '/dist/' in str(path):
            continue
        try:
            chunks.append(path.read_text(encoding='utf-8', errors='ignore'))
        except OSError:
            continue
    return '\n'.join(chunks)


def collect_route_paths(routes_file: Path) -> list:
    text = routes_file.read_text(encoding='utf-8', errors='ignore')
    paths = re.findall(r'path\s*[:=]\s*["\']([^"\']+)["\']', text)
    return sorted(set(paths))


def collect_route_entries(routes_file: Path) -> tuple:
    text = routes_file.read_text(encoding='utf-8', errors='ignore')
    chunks = re.split(r'<Route\b', text)
    renderable, redirects = set(), set()
    for chunk in chunks[1:]:
        match = re.search(r'path\s*=\s*["\']([^"\']+)["\']', chunk)
        if not match:
            continue
        path = match.group(1)
        body = chunk.split('</Route>')[0]
        if 'Navigate' in body:
            redirects.add(path)
        else:
            renderable.add(path)
    if not renderable:
        renderable = set(re.findall(r'path\s*[:=]\s*["\']([^"\']+)["\']', text))
    return sorted(renderable), sorted(redirects)


def is_catchall_route(route_path: str) -> bool:
    return route_path in ('*', '/*')


def meaningful_routes(renderable_paths: list[str]) -> list[str]:
    return [p for p in renderable_paths if not is_catchall_route(p)]


def route_matches(route_path: str, candidate: str) -> bool:
    if is_catchall_route(route_path):
        return False
    if route_path == candidate:
        return True
    if route_path.endswith('/*'):
        return candidate.startswith(route_path[:-1])
    return False


def format_grouped_errors(errors: list[str], limit_per_group: int = 8) -> str:
    groups: dict[str, list[str]] = {}
    for message in errors:
        match = re.match(r'\[判据(\d+)\]', message)
        key = match.group(1) if match else '0'
        groups.setdefault(key, []).append(message)
    lines: list[str] = []
    for key in sorted(groups.keys(), key=lambda item: int(item) if item.isdigit() else 99):
        items = groups[key]
        lines.append(f'【判据{key}】共 {len(items)} 条')
        for item in items[:limit_per_group]:
            lines.append(f'  - {item}')
        if len(items) > limit_per_group:
            lines.append(f'  … 另有 {len(items) - limit_per_group} 条')
    return '\n'.join(lines)


def tab_is_substantive(key: str, body: str) -> bool:
    if key == 'field' and '本块不涉及字段' in body.replace(' ', ''):
        return True
    return not is_empty_tab_body(body)


def route_matcher_hits_route_table(pattern: re.Pattern[str], meaningful: list[str]) -> bool:
    return any(pattern.search(path) for path in meaningful)


def validate_page_on_routes(
    page: str,
    label: str,
    meaningful: list[str],
    renderable_paths: list[str],
    redirect_paths: list[str],
) -> tuple[list[str], list[str], bool]:
    """校验 page 是否在真实路由表。返回 (errors, warnings, page_route_ok)。

    page_route_ok：page 已落在真实路由（含仅 warning 的前缀通配/参数路由），
    才允许用 pattern.search(page) 辅助判断 routeMatcher 是否有效；不得用假 page 给 matcher 洗白。
    """
    errors: list[str] = []
    warnings: list[str] = []
    if page == '*':
        return errors, warnings, True
    if any(route_matches(path, page) for path in meaningful):
        return errors, warnings, True
    if redirect_paths and any(route_matches(path, page) for path in redirect_paths):
        errors.append(f'[判据2] {label} page 为重定向路由，页面不会渲染')
        return errors, warnings, False
    if ':' in page:
        prefix = page.split(':', 1)[0]
        if any(p.startswith(prefix) for p in meaningful):
            warnings.append(f'{label} page {page} 为参数路由，建议写 routeMatcher 明确覆盖')
            return errors, warnings, True
    if any(
        not is_catchall_route(path) and path.endswith('/*') and page.startswith(path[:-1])
        for path in renderable_paths
    ):
        warnings.append(f'{label} page {page} 由前缀通配路由覆盖，建议写 routeMatcher 明确范围')
        return errors, warnings, True
    errors.append(f'[判据2] {label} page 不在真实路由表（已排除 *、/* 兜底）')
    return errors, warnings, False


def check_routes(annots: list[dict], renderable_paths: list[str], redirect_paths: list[str]) -> tuple[list[str], list[str]]:
    meaningful = meaningful_routes(renderable_paths)
    errors: list[str] = []
    warnings: list[str] = []
    for a in annots:
        page = str(a.get('page') or '')
        matcher = str(a.get('routeMatcher') or '').strip()
        label = block_label(a)
        if page in redirect_paths:
            errors.append(f'[判据2] {label} page 为重定向路由，页面不会渲染')
            continue
        if matcher:
            try:
                pattern = re.compile(matcher)
            except re.error:
                errors.append(f'[判据2] {label} routeMatcher 非法正则: /{matcher}/')
                continue
            page_errs, page_warns, page_route_ok = validate_page_on_routes(
                page, label, meaningful, renderable_paths, redirect_paths
            )
            errors.extend(page_errs)
            warnings.extend(page_warns)
            hits_table = route_matcher_hits_route_table(pattern, meaningful)
            hits_page = (
                page_route_ok
                and page
                and page != '*'
                and pattern.search(page)
            )
            if not hits_table and not hits_page:
                errors.append(
                    f'[判据2] {label} routeMatcher /{matcher}/ 未命中任何真实路由（已排除 *、/* 兜底）'
                )
            if page and page != '*' and not pattern.search(page):
                errors.append(
                    f'[判据2] {label} routeMatcher 未覆盖本块 page（过窄，例如只匹配 create 漏 edit/）'
                )
            continue
        if page == '*':
            continue
        page_errs, page_warns, _ = validate_page_on_routes(
            page, label, meaningful, renderable_paths, redirect_paths
        )
        errors.extend(page_errs)
        warnings.extend(page_warns)
    return errors, warnings


def selector_anchor(selector: str) -> str:
    match = re.search(r'data-anno\s*=\s*["\']?([\w-]+)', selector)
    if match:
        return match.group(1)
    match = re.search(r"\[data-anno=['\"]?([\w-]+)", selector)
    return match.group(1) if match else ''


def screen_state(annotation: dict) -> str:
    value = str(annotation.get('screenState') or 'host').strip()
    return value or 'host'


def id_group_key(annotation: dict) -> str:
    matcher = annotation.get('routeMatcher') or annotation.get('page') or ''
    return f"{matcher}::{screen_state(annotation)}"


def block_label(annotation: dict) -> str:
    return f"{annotation.get('page')}#{annotation.get('id')} screenState={screen_state(annotation)}"


OVERLAY_SCOPE_PREFIXES = ('弹窗', '抽屉', '弹层')


def scope_label_requires_overlay_state(scope_label: str) -> bool:
    text = str(scope_label or '').strip()
    return any(text.startswith(prefix) for prefix in OVERLAY_SCOPE_PREFIXES)


def suggested_overlay_screen_state(scope_label: str) -> str:
    text = str(scope_label or '').strip()
    if text.startswith('弹窗'):
        kind = 'modal'
    elif text.startswith('抽屉'):
        kind = 'drawer'
    else:
        kind = 'overlay'
    detail = re.sub(r'^弹窗|^抽屉|^弹层', '', text).lstrip('：:').strip() or 'state'
    token = re.sub(r'[/\s]+', '-', detail)
    token = re.sub(r'[^\w\-一-龥]', '', token)[:40] or 'state'
    return f'{kind}-{token}'


def check_screen_state_attribution(annots: list[dict]) -> list[str]:
    errors: list[str] = []
    for a in annots:
        scope = str(a.get('scopeLabel') or '').strip()
        if not scope_label_requires_overlay_state(scope):
            continue
        if screen_state(a) != 'host':
            continue
        label = block_label(a)
        suggested = suggested_overlay_screen_state(scope)
        errors.append(
            f'[判据11] {label}: scopeLabel「{scope}」为叠加态，当前 screenState=host（或未填）；'
            f'应改为独立 screenState（建议 {suggested}，与同弹窗/抽屉各块共用同一值）'
        )
    return errors


def parse_prd_pages(raw: str) -> list[str]:
    parts = re.split(r'[,，\n]+', raw or '')
    return [p.strip() for p in parts if p.strip()]


def numeric_ids(ids: list[str]) -> list[int]:
    out = []
    for item in ids:
        if re.fullmatch(r'\d+', str(item)):
            out.append(int(item))
    return sorted(out)


def check_field_tab(annotation: dict, body: str) -> Optional[str]:
    if '本块不涉及字段' in body.replace(' ', ''):
        return None
    if is_empty_tab_body(body):
        return '字段说明为空或仅「暂无」，须为四列表格或「本块不涉及字段」'
    if POINTER_PHRASE.search(body):
        return '字段说明出现「见§/参见」指路'
    if FIELD_TABLE_HEADER.search(body):
        return None
    if count_markdown_items(body) > 0 and '|' not in body:
        return '字段说明应为四列表格或「本块不涉及字段」，当前为散文'
    if body.strip() and '|' in body and not FIELD_TABLE_HEADER.search(body):
        return '字段说明表格表头须为：字段名称 / 是否必填 / 是否可编辑 / 约束与校验'
    return None


def check_annotation_markdown(annotation: dict) -> list[str]:
    errors = []
    label = block_label(annotation)
    md = str(annotation.get('markdown') or '')
    if DISPLAY_SOURCE.search(md):
        errors.append(f'[判据7] {label} 页签「全文」: Markdown 含展示用来源行，应只写在 sourceRefs')
    sections = parse_annotation_tabs(md)
    for key in TAB_KEYS:
        body = tab_body(sections, key)
        if key == 'field':
            field_err = check_field_tab(annotation, body)
            if field_err:
                errors.append(f'[判据6] {label} 页签「字段说明」: {field_err}')
        if is_empty_tab_body(body):
            continue
        count = count_markdown_items(body)
        if count == 0 and len(body.strip()) > 8:
            tab_name = {'page': '页面内容', 'interaction': '交互说明', 'rule': '业务规则', 'field': '字段说明', 'pending': '待确认'}[key]
            errors.append(f'[判据5] {label} 页签「{tab_name}」: 有正文但条目统计为 0（与 runtime 解析不一致）')
    substantive = sum(1 for key in TAB_KEYS if tab_is_substantive(key, tab_body(sections, key)))
    if substantive < 2:
        errors.append(
            f'[判据8] {label}: 实质有内容的页签仅 {substantive} 个（须至少 2 个）；'
            f'字段说明写「本块不涉及字段」计为有内容'
        )
    return errors


def check_id_groups(annots: list[dict]) -> list[str]:
    errors = []
    groups: dict[str, list[dict]] = {}
    for a in annots:
        groups.setdefault(id_group_key(a), []).append(a)
    for group_key, items in groups.items():
        ids = [str(a.get('id')) for a in items]
        dup = sorted({i for i in ids if ids.count(i) > 1})
        if dup:
            sample = block_label(items[0])
            errors.append(
                f'[判据3] {sample} 等同编号分组内 id 重复: {dup}（分组键 {group_key})'
            )
        nums = numeric_ids(ids)
        if nums:
            expected = list(range(1, len(nums) + 1))
            if nums != expected or len(nums) != len(items):
                errors.append(
                    f'[判据4] 分组 {group_key} 内 id 须从 1 连续: 当前 {nums}'
                )
    return errors


def check_source_refs(config: dict, annots: list[dict]) -> list[str]:
    errors = []
    requirements = {str(r.get('id')): r for r in config.get('sourceRequirements', []) if r.get('id')}
    for a in annots:
        label = block_label(a)
        refs = a.get('sourceRefs') or []
        if not refs:
            errors.append(f'[判据9] {label}: sourceRefs 为空')
            continue
        for ref in refs:
            ref_s = str(ref)
            if ref_s not in requirements:
                errors.append(f'[判据9] {label}: sourceRefs 引用不存在的需求点 {ref_s}')
    mapped = set()
    for a in annots:
        for ref in a.get('sourceRefs') or []:
            mapped.add(str(ref))
    for req_id in requirements:
        if req_id not in mapped:
            errors.append(f'[判据9] 需求点 {req_id} 未被任何标注 sourceRefs 覆盖')
    return errors


def check_prd_pages(annots: list[dict], prd_pages: list[str]) -> list[str]:
    if not prd_pages:
        return []
    errors = []
    allowed = set(prd_pages)
    for a in annots:
        page = str(a.get('page') or '')
        if page == '*':
            continue
        if page not in allowed:
            errors.append(
                f'[判据10] {block_label(a)}: page {page} 不在本 PRD 页面清单内'
            )
    return errors


def check_assets(
    directory: Path,
    src: Optional[Path] = None,
    routes_file: Optional[Path] = None,
    config_path: Optional[Path] = None,
    prd_pages: Optional[list[str]] = None,
) -> dict:
    for name in ('runtime.js', 'runtime.css', 'annotation.bundle.json'):
        p = directory / name
        if not p.is_file() or not p.stat().st_size:
            raise ValueError(f'Missing or empty asset: {p}')
    bundle = json.loads((directory / 'annotation.bundle.json').read_text(encoding='utf-8'))
    annots = bundle.get('annotations')
    if not isinstance(annots, list) or not annots:
        raise ValueError('Bundle has no annotations')

    errors: list[str] = []
    seen = set()
    for a in annots:
        key = (a.get('page'), screen_state(a), a.get('id'))
        if key in seen:
            errors.append(f'[判据3] 同一 page/screenState 下 id 重复: {key}')
        seen.add(key)

    errors.extend(check_id_groups(annots))
    errors.extend(check_screen_state_attribution(annots))

    for a in annots:
        if a.get('markdownFile'):
            raise ValueError(f'Annotation {a.get("id")} still references source markdown; compile before publishing')
        if not a.get('markdown'):
            raise ValueError(f'Annotation {a.get("id")} missing compiled markdown')
        if not a.get('target') and a.get('type') != 'page-global':
            raise ValueError(f'Annotation {a.get("id")} missing target selector')
        errors.extend(check_annotation_markdown(a))

    if not bundle.get('coverage'):
        raise ValueError('Bundle missing coverage export')

    warnings: list[str] = []
    result = {
        'annotations': len(annots),
        'pages': len({a.get('page') for a in annots}),
        'version': bundle.get('version'),
        'coverage': bundle.get('coverage'),
    }

    if src:
        if not src.is_dir():
            raise ValueError(f'--src is not a directory: {src}')
        source_text = collect_source_text(src)
        missing = []
        for a in annots:
            if a.get('type') == 'page-global':
                continue
            target = a.get('target') or {}
            selectors = [target.get('selector') or ''] + list(target.get('fallbackSelectors') or [])
            selectors = [s for s in selectors if s]
            anchors = [selector_anchor(s) for s in selectors]
            anchors = [x for x in anchors if x]
            if anchors and not any(anchor in source_text for anchor in anchors):
                missing.append(f'[判据1] {block_label(a)} 锚点 {"/".join(anchors)} 在源码中不存在')
        errors.extend(missing)
        result['anchors_checked'] = len([a for a in annots if a.get('type') != 'page-global'])

    if routes_file:
        if not routes_file.is_file():
            raise ValueError(f'--routes is not a file: {routes_file}')
        route_paths = collect_route_paths(routes_file)
        renderable_paths, redirect_paths = collect_route_entries(routes_file)
        if not route_paths:
            raise ValueError(f'No route path found in {routes_file}')
        route_errors, route_warnings = check_routes(annots, renderable_paths, redirect_paths)
        errors.extend(route_errors)
        warnings.extend(route_warnings)
        result['routes_checked'] = len(route_paths)

    if config_path:
        if not config_path.is_file():
            raise ValueError(f'--config is not a file: {config_path}')
        config = json.loads(config_path.read_text(encoding='utf-8'))
        errors.extend(check_source_refs(config, annots))
        if prd_pages:
            errors.extend(check_prd_pages(annots, prd_pages))

    if errors:
        raise ValueError(format_grouped_errors(errors))

    if warnings:
        result['warnings'] = warnings[:12]
    return result


def main():
    ap = argparse.ArgumentParser(description='Validate prototype annotation deploy assets.')
    ap.add_argument('directory', help='annotation-kit dir, e.g. public/annotation-kit')
    ap.add_argument('--src', help='frontend source dir')
    ap.add_argument('--routes', help='router file, e.g. src/App.tsx')
    ap.add_argument('--config', help='annotation.config.json for sourceRefs / PRD scope')
    ap.add_argument('--prd-pages', help='comma or newline separated allowed pages for this PRD')
    args = ap.parse_args()
    prd_pages = parse_prd_pages(args.prd_pages) if args.prd_pages else None
    report = check_assets(
        Path(args.directory).resolve(),
        Path(args.src).resolve() if args.src else None,
        Path(args.routes).resolve() if args.routes else None,
        Path(args.config).resolve() if args.config else None,
        prd_pages,
    )
    print('Deployment assets valid: ' + json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(f'Annotation assets invalid:\n{error}') from error
