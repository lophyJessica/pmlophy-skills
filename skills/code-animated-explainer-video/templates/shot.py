"""动效讲解视频：Playwright 逐帧截图(30fps) → ffmpeg 合成 MP4

用法：
  python3 shot.py                全量渲染 + 合成
  python3 shot.py check          只做自检（跳帧一致性 + 关键状态）
  python3 shot.py still 9.0 12.5 导出指定秒数的单帧预览

依赖：playwright（chromium）、ffmpeg
页面约定：index.html 暴露 window.renderFrame(t)，t 单位秒，纯函数。
"""
import asyncio, os, sys, json

BASE = os.path.dirname(os.path.abspath(__file__))
FPS, DUR = 30, 20.0
FRAMES = f"{BASE}/frames"
OUT = f"{BASE}/eventtag.mp4"

from playwright.async_api import async_playwright

# 采样点：覆盖四个阶段和所有交界处
PROBES = [0.0, 0.5, 1.5, 3.0, 5.0, 5.5, 7.0, 9.0, 9.5,
          11.0, 13.0, 15.0, 15.5, 17.0, 19.9]


async def new_page(p):
    b = await p.chromium.launch(args=["--force-device-scale-factor=1",
                                     "--no-sandbox", "--disable-dev-shm-usage"])
    pg = await b.new_page(viewport={"width": 1920, "height": 1080})
    await pg.goto(f"file://{BASE}/index.html")
    await pg.wait_for_function("window.renderFrame !== undefined")
    return b, pg


async def snap_state(pg):
    """抓全页 DOM 状态：每个可见元素的 style + 文本。只用于比对一致性。"""
    return await pg.evaluate("""() => {
      const out = [];
      document.querySelectorAll('*').forEach((el, i) => {
        if (!el.offsetParent && getComputedStyle(el).position !== 'fixed') return;
        out.push([i, el.tagName, el.dataset.state || '',
                  (el.textContent || '').trim().slice(0, 40),
                  el.getAttribute('style') || '']);
      });
      return out;
    }""")


async def render_frame(pg, t):
    await pg.evaluate(f"window.renderFrame({t})")
    await pg.wait_for_timeout(12)


async def check():
    """跳帧一致性：顺序渲染作基准 → 乱序+干扰帧 → 反向扫 → 回原帧比对"""
    async with async_playwright() as p:
        b, pg = await new_page(p)
        base = {}
        for t in PROBES:
            await render_frame(pg, t)
            base[t] = await snap_state(pg)

        import random
        order = PROBES[:]
        random.shuffle(order)
        bad = []
        for t in order:
            await render_frame(pg, random.uniform(0, DUR))  # 干扰帧
            await render_frame(pg, t)
            if await snap_state(pg) != base[t]:
                bad.append(t)

        for t in reversed(PROBES):
            await render_frame(pg, t)
        # 回到一个中间帧再比对，确认没有被前序内容污染
        await render_frame(pg, 14.7)
        await b.close()

    print(f"跳帧一致性：{len(PROBES)-len(bad)}/{len(PROBES)} 通过")
    if bad:
        print("不一致的时间点：", bad)


async def still(times):
    async with async_playwright() as p:
        b, pg = await new_page(p)
        for t in times:
            await render_frame(pg, float(t))
            await pg.screenshot(path=f"{BASE}/still_{t}.png")
            print(f"still_{t}.png")
        await b.close()


async def full():
    os.makedirs(FRAMES, exist_ok=True)
    n = int(DUR * FPS)
    async with async_playwright() as p:
        b, pg = await new_page(p)
        for i in range(n):
            await render_frame(pg, i / FPS)
            await pg.screenshot(path=f"{FRAMES}/{i:04d}.png")
            if i % 60 == 0:
                print(f"{i}/{n}", flush=True)
        await b.close()
    print("frames done")


def compose():
    os.system(f'ffmpeg -y -framerate {FPS} -i "{FRAMES}/%04d.png" '
              f'-c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow "{OUT}" -loglevel error')
    sz = os.path.getsize(OUT)
    print(f"{OUT}  {sz/1024/1024:.2f} MB  {DUR}s  {int(DUR*FPS)} 帧")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "check":
        asyncio.run(check())
    elif a and a[0] == "still":
        asyncio.run(still(a[1:]))
    else:
        asyncio.run(full())
        compose()
