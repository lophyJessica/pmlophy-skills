#!/usr/bin/env python3
"""一条命令出「整页截图 + 红虚线框 + 四边校验」的 PRD 用图。

为什么有它：2026-11-24 重拍 4 张图时，视口覆盖静默失效、坐标混用、虚线过稀、
框被裁四条坑轮着踩，全靠现场调——下次还得重来。这个脚本把整套固化下来：
视口断言、滚动、量框、截图、画框、四边校验一次跑完，不达标就非 0 退出。

用法：
    # 最简单：框住一个带 data-anno 锚点的区域
    python3 shot_redbox.py --url URL --anno trigger-timing --out 3-6.png

    # 框住多个锚点的并集（如标题+内容一起圈）
    python3 shot_redbox.py --url URL --anno trigger-type --anno trigger-timing --out 3-10.png

    # 用任意 CSS 选择器
    python3 shot_redbox.py --url URL --selector ".engage-radio-card" --out a.png

    # 带操作：先把页面点到目标状态再拍
    python3 shot_redbox.py --url URL --anno engage-tag-filter --out 3-15.png \\
        --action "click=+ 筛选行为组" \\
        --action "select=预售订单行为" \\
        --action "fill=取值=双11预售"

动作语法（可重复，按顺序执行）：
    click=<按钮文字>            按可见文字点（优先精确匹配）
    clickcss=<css 选择器>       按选择器点
    clickin=<容器文字>=<按钮>   在包含该文字的最小容器里点按钮（列表行、卡片均适用）
    select=<选项文字>           在页面里找含该选项的 select 并选中
    selectcss=<css>=<选项文字>  指定 select
    fill=<placeholder>=<值>     按占位符填值（React 受控组件已处理）
    wait=<毫秒>

退出码：0 成功且四边校验通过；1 校验失败或出错（不交付不合格的图）。
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

RED = (220, 38, 38)
BOX_W = 4         # 线宽：3px 在 1600 宽图上缩放后像断线
DASH, GAP = 12, 4  # 占空比 75%；低于 70% 视觉上就成碎段
PAD = 8
VIEW_W, VIEW_H = 1600, 1000


def dashed_rect(d, box):
    x0, y0, x1, y1 = box

    def seg(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = max(abs(dx), abs(dy))
        if length <= 0:
            return
        s = 0.0
        while s < length:                      # 不用整除，否则末尾一段会丢
            e = min(s + DASH, length)
            d.line([(a[0] + dx * s / length, a[1] + dy * s / length),
                    (a[0] + dx * e / length, a[1] + dy * e / length)],
                   fill=RED, width=BOX_W)
            s += DASH + GAP

    seg((x0, y0), (x1, y0))
    seg((x1, y0), (x1, y1))
    seg((x1, y1), (x0, y1))
    seg((x0, y1), (x0, y0))
    for cx, cy in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)   # 四角压实


def four_edges_ratio(path, box):
    im = Image.open(path).convert('RGB')
    px = im.load()
    x0, y0, x1, y1 = box

    def red(x, y):
        if 0 <= x < im.width and 0 <= y < im.height:
            r, g, b = px[x, y][:3]
            return abs(r - RED[0]) < 70 and abs(g - RED[1]) < 70 and abs(b - RED[2]) < 70
        return False

    def rh(y, xa, xb):
        return sum(1 for x in range(xa, xb + 1) for dy in range(-3, 4) if red(x, y + dy)) / max(1, (xb - xa + 1) * 7)

    def rv(x, ya, yb):
        return sum(1 for y in range(ya, yb + 1) for dx in range(-3, 4) if red(x + dx, y)) / max(1, (yb - ya + 1) * 7)

    return rh(y0, x0, x1), rh(y1, x0, x1), rv(x0, y0, y1), rv(x1, y0, y1)


def do_action(page, spec):
    if spec.startswith('wait='):
        page.wait_for_timeout(int(spec[5:]))
    elif spec.startswith('clickcss='):
        page.click(spec[9:], timeout=8000)
    elif spec.startswith('click='):
        text = spec[6:]
        loc = page.get_by_text(text, exact=True)
        if loc.count() == 0:
            loc = page.get_by_text(text)
        loc.first.click(timeout=8000)
    elif spec.startswith('clickin='):
        # 在“包含某段文字的最小容器”里点按钮——列表页每行都有同名「编辑」按钮，
        # 直接 click=编辑 会点到第一行（实测踩过），必须缩到目标卡片内
        container, _, btn = spec[8:].partition('=')
        page.evaluate("""([c, b]) => {
            const cands = [...document.querySelectorAll('*')]
                .filter(e => (e.textContent || '').includes(c))
                .sort((a, b2) => a.textContent.length - b2.textContent.length);
            if (!cands.length) throw new Error('找不到包含该文字的容器: ' + c);
            for (const el of cands) {
                const t = [...el.querySelectorAll('button,a,span,div')]
                    .filter(e => (e.textContent || '').trim() === b).pop();
                if (t) { t.click(); return; }
            }
            throw new Error('从最小容器往上都找不到按钮: ' + b);
        }""", [container, btn])
    elif spec.startswith('selectcss='):
        css, _, opt = spec[10:].partition('=')
        page.select_option(css, label=opt, timeout=8000)
    elif spec.startswith('select='):
        text = spec[7:]
        page.evaluate("""(t) => {
            const sel = [...document.querySelectorAll('select')]
                .find(s => [...s.options].some(o => o.text.trim().includes(t)));
            if (!sel) throw new Error('找不到含该选项的 select: ' + t);
            const opt = [...sel.options].find(o => o.text.trim().includes(t));
            const setter = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value').set;
            setter.call(sel, opt.value);
            sel.dispatchEvent(new Event('change', {bubbles: true}));
        }""", text)
    elif spec.startswith('fill='):
        holder, _, val = spec[5:].partition('=')
        page.evaluate("""([h, v]) => {
            const inp = [...document.querySelectorAll('input')].find(i => i.placeholder === h);
            if (!inp) throw new Error('找不到 placeholder=' + h);
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
            setter.call(inp, v);
            inp.dispatchEvent(new Event('input', {bubbles: true}));
            inp.dispatchEvent(new Event('change', {bubbles: true}));
        }""", [holder, val])
    else:
        raise SystemExit('无法识别的动作: ' + spec)
    page.wait_for_timeout(800)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--anno', action='append', default=[], help='data-anno 值，可多个取并集')
    ap.add_argument('--selector', action='append', default=[], help='任意 CSS 选择器')
    ap.add_argument('--action', action='append', default=[], help='操作，见文件头说明')
    ap.add_argument('--scroll-gap', type=int, default=40, help='框上边缘离图顶的距离')
    ap.add_argument('--hide', action='append', default=[], help='截图前隐藏的元素，css 选择器')
    ap.add_argument('--keep-full', action='store_true', help='不做滚动对齐，直接截当前视口')
    args = ap.parse_args()

    selectors = ['[data-anno="%s"]' % a for a in args.anno] + args.selector
    if not selectors:
        raise SystemExit('至少给一个 --anno 或 --selector')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': VIEW_W, 'height': VIEW_H})
        page.goto(args.url, wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(2500)

        # 视口断言：所有坐标的前提
        vw, vh = page.evaluate('[innerWidth, innerHeight]')
        if (vw, vh) != (VIEW_W, VIEW_H):
            raise SystemExit('视口不是 %dx%d，实际 %dx%d' % (VIEW_W, VIEW_H, vw, vh))

        for act in args.action:
            do_action(page, act)
        page.wait_for_timeout(1200)

        for css in args.hide:
            page.evaluate("c => document.querySelectorAll(c).forEach(e => e.style.display='none')", css)

        # 滚到目标区域，并按 --scroll-gap 对齐
        page.evaluate("""(sels) => {
            const els = sels.map(s => document.querySelector(s)).filter(Boolean);
            if (!els.length) throw new Error('找不到锚点: ' + sels.join(','));
            const top = Math.min(...els.map(e => e.getBoundingClientRect().top + window.scrollY));
            window.scrollTo(0, Math.max(0, top - %d));
        }""" % args.scroll_gap, selectors)
        page.wait_for_timeout(1800)

        rects = page.evaluate("""(sels) => sels.map(s => {
            const e = document.querySelector(s);
            if (!e) return null;
            const r = e.getBoundingClientRect();
            return {x: r.x, y: r.y, w: r.width, h: r.height, top: r.top + window.scrollY};
        })""", selectors)
        rects = [r for r in rects if r]
        if not rects:
            raise SystemExit('锚点全都没命中')

        if args.keep_full:
            page.evaluate('window.scrollTo(0, 0)')
            page.wait_for_timeout(600)
            rects = page.evaluate("""(sels) => sels.map(s => {
                const e = document.querySelector(s);
                if (!e) return null;
                const r = e.getBoundingClientRect();
                return {x: r.x, y: r.y, w: r.width, h: r.height};
            })""", selectors)
            rects = [r for r in rects if r]

        x0 = min(r['x'] for r in rects) - PAD
        y0 = min(r['y'] for r in rects) - PAD
        x1 = max(r['x'] + r['w'] for r in rects) + PAD
        y1 = max(r['y'] + r['h'] for r in rects) + PAD
        x0, y0 = max(0, int(x0)), max(0, int(y0))
        x1, y1 = min(VIEW_W - 1, int(x1)), min(VIEW_H - 1, int(y1))

        if x1 <= x0 or y1 <= y0:
            raise SystemExit('框退化: %r' % ((x0, y0, x1, y1),))

        raw = str(Path(args.out).with_suffix('.raw.png'))
        page.screenshot(path=raw)          # 整视口截图，坐标即视口坐标，无需 clip
        browser.close()

    im = Image.open(raw).convert('RGB')
    dashed_rect(ImageDraw.Draw(im), (x0, y0, x1, y1))
    im.save(args.out)
    Path(raw).unlink(missing_ok=True)

    top, bot, left, right = four_edges_ratio(args.out, (x0, y0, x1, y1))
    worst = min(top, bot, left, right)
    print('%s  %dx%d  框 (%d,%d)-(%d,%d)' % (args.out, im.width, im.height, x0, y0, x1, y1))
    print('  上 %.0f%% | 下 %.0f%% | 左 %.0f%% | 右 %.0f%%' % (top * 100, bot * 100, left * 100, right * 100))
    if worst < 0.45:
        print('  ✗ 四边不完整，不交付')
        sys.exit(1)
    print('  ✓ 四边完整')


if __name__ == '__main__':
    main()
