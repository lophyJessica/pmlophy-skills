#!/usr/bin/env python3
"""评审PRD整页红框图批量截图脚本。
读 annotation.config.json 拿每个角标的 data-anno selector + 页路由，
用 Playwright 打开线上原型、拿到各 anchor 的 bounding box、整页截图，
再用 Pillow 画红虚线框圈选该角标区域，逐角标生成"整页+红框"图。
本地 agent 填好下方 CONFIG 即可跑通，无需理解 data-anno/Playwright 细节。

用法:
  python3 capture_orm.py --project-dir <forge-scrm根> --out-dir images --base-url https://pmlophy.com/project/forge-crm/#
需先: pip install playwright pillow  (或 PIP_BREAK_SYSTEM_PACKAGES=1 pip install ...)
      python3 -m playwright install chromium  (或指已有浏览器,见 CHROME 常量)
"""
import argparse, json, os, re, sys, time
from PIL import Image, ImageDraw

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("缺少 playwright: pip install playwright")

# ---- 环境常量（本地 agent 根据机器调整）----
# 优先自动发现系统缓存浏览器，找不到则用 playwright 自带
import glob
_DEFAULT_CHROME_CANDIDATES = [
    "/root/.cache/ms-playwright/chromium-*/chrome-linux/chrome",
    "/root/.cache/ms-playwright/chromium-*/chrome-linux/chrome",
]
def _find_chrome():
    for pat in _DEFAULT_CHROME_CANDIDATES:
        hits = glob.glob(pat)
        if hits:
            return hits[-1]
    return None  # 交给 playwright 默认

RED = (220, 38, 38)  # 红虚线框颜色


def dashed_rect(d, box, color=RED, width=3, dash=8, gap=4):
    """在 ImageDraw 上画虚线矩形（不依赖外框，自己分段画）。box=(x0,y0,x1,y1)"""
    x0, y0, x1, y1 = box

    def seg(a0, b0):
        dx, dy = b0[0] - a0[0], b0[1] - a0[1]
        L = max(abs(dx), abs(dy))
        if L == 0:
            return
        n = L // (dash + gap)
        for i in range(n + 1):
            s = i * (dash + gap)
            d.line([(a0[0] + dx * s / L, a0[1] + dy * s / L),
                    (a0[0] + dx * min(s + dash, L) / L, a0[1] + dy * min(s + dash, L) / L)],
                   fill=color, width=width)
    seg((x0, y0), (x1, y0))
    seg((x1, y0), (x1, y1))
    seg((x1, y1), (x0, y1))
    seg((x0, y1), (x0, y0))


def load_anno_config(config_path):
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


class CaptureTask:
    """一个角标的截图任务。mode: page_whole(整页无框=页面级) | area(锚点区域红框) | modal(触发弹窗)"""
    def __init__(self, anno_id, page, selector, modal_trigger=None, page_whole=False,
                 view_switcher=None, mode="area"):
        self.anno_id = anno_id
        self.page = page            # url 形如 "#/opportunities"
        self.selector = selector    # data-anno selector
        self.modal_trigger = modal_trigger  # 由本地agent提供: 触发弹窗的CSS选择器或文本
        self.page_whole = page_whole
        self.view_switcher = view_switcher  # 形如 "列表视图"/"看板视图" 按钮title, 需切换时填
        self.mode = mode


def build_tasks(config, page_map=None):
    """从 annotation.config.json 自动生成任务清单。
    page_map: {路由: 真实URL} 覆盖 config 里的 page 字段。页面级角标(type=page/page-global)截整页。
    弹窗角标(type=interaction 且 selector 出现在 modal 白名单)需手动在 tasks 里补 modal_trigger。
    """
    tasks = []
    sel_set = set()
    for a in config["annotations"]:
        page = a.get("page", "")
        # 取对应页面默认 URL
        real_page = page_map.get(page, page) if page_map else page
        sel = a["target"]["selector"] if a.get("target") else None
        if not sel:
            continue
        ttype = a.get("type", "")
        page_whole = ttype in ("page", "page-global")
        tasks.append(CaptureTask(a["id"], real_page, sel, page_whole=page_whole))
    return tasks


def resolve_path(base_url, page):
    # page 形如 "#/opportunities" 或 "/opportunities"；拼到 base_url 后
    p = page.lstrip('/')
    if not p.startswith('#'):
        p = '#' + (p if p.startswith('/') else '/' + p)
    return base_url.rstrip('/') + '/' + p.lstrip('#')


def run(args):
    config = load_anno_config(args.config)
    os.makedirs(args.out_dir, exist_ok=True)

    # 从 config 拿每页的 data-anno selector 集合（用于批量探测）
    # 也支持直接传 --tasks 手动清单（跳过自动构建）
    tasks = build_tasks(config) if not args.task_json else [
        CaptureTask(t["id"], t["page"], t["selector"], page_whole=t.get("page_whole", False),
                    modal_trigger=t.get("modal_trigger"))
        for t in json.loads(args.task_json)
    ]
    print(f"待截图任务: {len(tasks)} 个")

    chrome = args.chrome or _find_chrome()
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, executable_path=chrome,
                              args=["--no-sandbox", "--disable-dev-shm-usage"])
        page = b.new_page(viewport={"width": 1440, "height": 900})
        results = []
        for task in tasks:
            url = resolve_path(args.base_url, task.page)
            try:
                page.goto(url, timeout=60000, wait_until="networkidle")
                page.wait_for_timeout(args.wait or 2500)
                # 视图切换（若需要）
                if task.view_switcher:
                    page.evaluate(
                        f"""() => {{ const el=document.querySelector("[data-anno-action='{task.view_switcher}']"); if(el) el.click() }}""")
                    page.wait_for_timeout(1200)
                # 取 anchor
                box = page.evaluate(
                    "(sel)=>{const el=document.querySelector(sel);if(!el)return null;"
                    "const r=el.getBoundingClientRect();return{x:Math.round(r.x),y:Math.round(r.y+window.scrollY),w:Math.round(r.width),h:Math.round(r.height)}}",
                    f"[data-anno='{task.selector}']")
                if box is None and not task.page_whole:
                    print(f"  ⚠ {task.anno_id} 锚点 {task.selector} 未取到（可能需交互/弹窗/页面未加载）")
                    results.append({"id": task.anno_id, "ok": False, "reason": "anchor_null"})
                    continue

                # 截图整页
                shot_path = os.path.join(args.out_dir, "tmp_base.png")
                page.screenshot(path=shot_path, full_page=False)

                # 页面级 -> 整页无框（直接复制）；区域 -> 画红框
                if task.page_whole:
                    final_path = os.path.join(args.out_dir, f"{args.name_prefix or ''}{task.anno_id}.png")
                    import shutil
                    shutil.copy(shot_path, final_path)
                    print(f"  ✓ {task.anno_id} 整页")
                else:
                    pad = 6
                    box2 = (box["x"] - pad, box["y"] - pad, box["x"] + box["w"] + pad, box["y"] + box["h"] + pad)
                    img = Image.open(shot_path)
                    d = ImageDraw.Draw(img)
                    dashed_rect(d, box2)
                    final_path = os.path.join(args.out_dir, f"{args.name_prefix or ''}{task.anno_id}.png")
                    img.save(final_path)
                    print(f"  ✓ {task.anno_id} 红框 @ ({box['x']},{box['y']}) {box['w']}x{box['h']}")
                results.append({"id": task.anno_id, "ok": True, "file": final_path})
            except Exception as e:
                print(f"  ✗ {task.anno_id} 失败: {e}")
                results.append({"id": task.anno_id, "ok": False, "reason": str(e)})
        b.close()

    print(f"\n成功 {sum(1 for r in results if r['ok'])}/{len(results)}")
    fails = [r for r in results if not r["ok"]]
    if fails:
        print("需人工处理（多为弹窗类）：")
        for f in fails:
            print(f"  - id {f['id']}: {f.get('reason')}")
    return 0 if not fails else 2


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="评审PRD整页红框图批量截图")
    ap.add_argument("--config", required=True, help="annotation.config.json 路径")
    ap.add_argument("--out-dir", required=True, help="输出图片目录")
    ap.add_argument("--base-url", required=True, help="原型根URL,如 https://pmlophy.com/project/forge-crm/#")
    ap.add_argument("--name-prefix", default="", help="图片名前缀,如 '商机列表页-'")
    ap.add_argument("--wait", type=int, default=2500, help="每页加载等待ms")
    ap.add_argument("--chrome", default=None, help="chrome可执行路径(默认自动找缓存)")
    ap.add_argument("--task-json", default=None, help="可选手动任务JSON,覆盖自动构建")
    sys.exit(run(ap.parse_args()))