#!/usr/bin/env python3
"""Check deployable prototype annotation assets.

No network or third-party dependencies. Validates the compiled annotation-kit dir:
bundle completeness, per-page unique ids, compiled-in markdown, target selectors, coverage.
This is NOT DOM mounting or remote hosting validation.

可选的路由/锚点静态校验（强烈建议在发版前加上）：

    --src    <前端源码目录>  每个 target.selector 里的 data-anno 值必须在源码中真实存在
    --routes <路由文件>      每个 page / routeMatcher 必须能命中路由表里的至少一条路由

这两项拦的是一类静默失败：标注写好了、编译通过了、页面上一颗角标都出不来。
2026-10 私域2.0 一期就踩过——菜单路由从 /auth/tags 改到 /engage/tags 后，
config 里的 page 没跟着改，编译校验全绿，线上 3 条标注直接消失。
"""
import argparse
import json
import re
from pathlib import Path
from typing import Optional

SOURCE_SUFFIXES = {'.tsx', '.ts', '.jsx', '.js', '.vue', '.html'}


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
    """Return (renderable_paths, redirect_paths).

    重定向路由（element={<Navigate .../>}）在路由表里“存在”，但页面永远不会渲染在
    那个 URL 上，把标注 page 指向它等于静默失效——必须单独识别出来。
    """
    text = routes_file.read_text(encoding='utf-8', errors='ignore')
    chunks = re.split(r'<Route\b', text)
    renderable, redirects = set(), set()
    for chunk in chunks[1:]:
        match = re.search(r'path\s*=\s*["\']([^"\']+)["\']', chunk)
        if not match:
            continue
        path = match.group(1)
        # 只看这条 Route 自身（到下一个 </Route> 或 /> 为止）
        body = chunk.split('</Route>')[0]
        if 'Navigate' in body:
            redirects.add(path)
        else:
            renderable.add(path)
    if not renderable:
        renderable = set(re.findall(r'path\s*[:=]\s*["\']([^"\']+)["\']', text))
    return sorted(renderable), sorted(redirects)


def route_matches(route_path: str, candidate: str) -> bool:
    """Whether a router entry can serve the given concrete URL path.

    A trailing ``/*`` is a wildcard route (e.g. /tools/* serving /tools/whats/friends),
    so it has to be matched by prefix, not by equality.
    """
    if route_path == candidate:
        return True
    if route_path.endswith('/*'):
        return candidate.startswith(route_path[:-1])
    if route_path == '*':
        return True
    return False


def selector_anchor(selector: str) -> str:
    match = re.search(r'data-anno\s*=\s*["\']?([\w-]+)', selector)
    if match:
        return match.group(1)
    match = re.search(r"\[data-anno=['\"]?([\w-]+)", selector)
    return match.group(1) if match else ''


def check_assets(directory: Path, src: Optional[Path] = None, routes_file: Optional[Path] = None) -> dict:
    for name in ('runtime.js', 'runtime.css', 'annotation.bundle.json'):
        p = directory / name
        if not p.is_file() or not p.stat().st_size:
            raise ValueError(f'Missing or empty asset: {p}')
    bundle = json.loads((directory / 'annotation.bundle.json').read_text(encoding='utf-8'))
    annots = bundle.get('annotations')
    if not isinstance(annots, list) or not annots:
        raise ValueError('Bundle has no annotations')
    seen = set()
    dups = []
    for a in annots:
        key = (a.get('page'), a.get('id'))
        if key in seen:
            dups.append(f'{a.get("page")}/{a.get("id")}')
        seen.add(key)
    if dups:
        raise ValueError(f'Duplicate annotation id per page: {sorted(set(dups))[:10]}')

    # 同一 routeMatcher 分组内 id 必须唯一：宿主页与弹窗共用一个 matcher 时，
    # 两组都从 1 开始编号会让页面上出现两个“1”，评审分不清角标对应哪里。
    by_matcher = {}
    for a in annots:
        matcher = a.get('routeMatcher') or a.get('page') or ''
        by_matcher.setdefault(matcher, []).append(str(a.get('id')))
    matcher_dups = {m: sorted({i for i in ids if ids.count(i) > 1}) for m, ids in by_matcher.items()}
    matcher_dups = {m: d for m, d in matcher_dups.items() if d}
    if matcher_dups:
        raise ValueError(
            f'Duplicate annotation id within the same route group (page+modal must share one id sequence): {matcher_dups}'
        )

    for a in annots:
        if a.get('markdownFile'):
            raise ValueError(f'Annotation {a.get("id")} still references source markdown; compile before publishing')
        if not a.get('markdown'):
            raise ValueError(f'Annotation {a.get("id")} missing compiled markdown')
        if not a.get('target'):
            raise ValueError(f'Annotation {a.get("id")} missing target selector')
    if not bundle.get('coverage'):
        raise ValueError('Bundle missing coverage export')

    warnings = []
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
            if not selectors:
                continue
            anchors = [selector_anchor(s) for s in selectors]
            anchors = [x for x in anchors if x]
            if anchors and not any(anchor in source_text for anchor in anchors):
                missing.append(f'{a.get("page")}#{a.get("id")} {"/".join(anchors)}')
        if missing:
            raise ValueError(
                'data-anno anchor not found in source (annotation can never mount): ' + '; '.join(missing[:12])
            )
        result['anchors_checked'] = len([a for a in annots if a.get('type') != 'page-global'])

    if routes_file:
        if not routes_file.is_file():
            raise ValueError(f'--routes is not a file: {routes_file}')
        route_paths = collect_route_paths(routes_file)
        renderable_paths, redirect_paths = collect_route_entries(routes_file)
        if not route_paths:
            raise ValueError(f'No route path found in {routes_file}')
        unmatched = []
        for a in annots:
            page = str(a.get('page') or '')
            matcher = a.get('routeMatcher') or ''
            if page in redirect_paths:
                unmatched.append(f'{page}#{a.get("id")} page is a redirect route (never renders); point at the real page')
                continue
            if matcher:
                pattern = re.compile(matcher)
                if any(pattern.search(p) for p in renderable_paths):
                    continue
                # 通配/参数路由（如 /tools/*）无法静态枚举出具体 URL：只要 page 落在
                # 这类路由下，就降级为提醒，而不是判死。
                if any(route_matches(p, page) for p in renderable_paths):
                    warnings.append(f'{page}#{a.get("id")} matcher /{matcher}/ not verifiable against wildcard routes')
                    continue
                if redirect_paths and any(route_matches(p, page) for p in redirect_paths):
                    unmatched.append(f'{page}#{a.get("id")} page is a redirect route (never renders); point at the real page')
                    continue
                unmatched.append(f'{page}#{a.get("id")} matcher /{matcher}/ matches no route')
                continue
            if any(route_matches(p, page) for p in renderable_paths):
                continue
            if redirect_paths and any(route_matches(p, page) for p in redirect_paths):
                unmatched.append(f'{page}#{a.get("id")} page is a redirect route (never renders); point at the real page')
                continue
            if ':' in page:
                prefix = page.split(':')[0]
                if any(p.startswith(prefix) for p in route_paths):
                    warnings.append(f'{page} relies on param route; add routeMatcher to be explicit')
                    continue
            unmatched.append(f'{page}#{a.get("id")} page not in router')
        if unmatched:
            raise ValueError('Annotation page cannot match any real route: ' + '; '.join(sorted(set(unmatched))[:12]))
        result['routes_checked'] = len(route_paths)

    if warnings:
        result['warnings'] = warnings[:12]
    return result


def main():
    ap = argparse.ArgumentParser(description='Validate prototype annotation deploy assets (not DOM mounting/hosting).')
    ap.add_argument('directory', help='annotation-kit dir, e.g. public/annotation-kit')
    ap.add_argument('--src', help='frontend source dir; verifies every data-anno anchor really exists')
    ap.add_argument('--routes', help='router file (e.g. src/App.tsx); verifies every page/routeMatcher hits a real route')
    args = ap.parse_args()
    report = check_assets(
        Path(args.directory).resolve(),
        Path(args.src).resolve() if args.src else None,
        Path(args.routes).resolve() if args.routes else None,
    )
    print('Deployment assets valid: ' + json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(f'Annotation assets invalid: {error}') from error
