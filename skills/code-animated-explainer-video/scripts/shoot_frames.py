import asyncio, os, sys, glob
from playwright.async_api import async_playwright

# 用法: python shoot_frames.py <html路径> <输出帧目录> [fps] [时长秒]
HTML = sys.argv[1] if len(sys.argv) > 1 else "motion-page.html"
OUT  = sys.argv[2] if len(sys.argv) > 2 else "./frames"
FPS  = int(sys.argv[3]) if len(sys.argv) > 3 else 30
DUR  = float(sys.argv[4]) if len(sys.argv) > 4 else 13.0


def find_chrome():
    """Playwright 包版本与已下载浏览器版本常对不上，直接复用缓存里的 chromium。"""
    hits = sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome")))
    return hits[-1] if hits else None


async def main():
    os.makedirs(OUT, exist_ok=True)
    chrome = find_chrome()
    args = ["--force-device-scale-factor=1", "--no-sandbox", "--disable-dev-shm-usage"]
    async with async_playwright() as p:
        if chrome:
            b = await p.chromium.launch(executable_path=chrome, args=args)
        else:
            b = await p.chromium.launch(args=args)   # 需先 playwright install chromium
        pg = await b.new_page(viewport={"width": 1920, "height": 1080})
        await pg.goto("file://" + os.path.abspath(HTML))
        await pg.wait_for_timeout(400)
        n = int(FPS * DUR)
        for i in range(n):
            await pg.evaluate("(t)=>window.renderFrame(t)", i / FPS)
            await pg.screenshot(path=f"{OUT}/f_{i:05d}.png")
            if i % 60 == 0:
                print(f"  {i}/{n}", flush=True)
        await b.close()
    print(f"完成 {n} 帧 → 合成: ffmpeg -y -framerate {FPS} -i {OUT}/f_%05d.png "
          f"-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart out.mp4")


asyncio.run(main())
