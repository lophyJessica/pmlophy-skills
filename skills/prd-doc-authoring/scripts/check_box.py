#!/usr/bin/env python3
"""校验 PRD 截图的红虚线框四边是否完整画出来。

为什么需要：虚线间隙一宽、线一细，图看着就像“断线/半框”，评审人一眼能看出来，
但尺寸、字节、甚至视觉模型都可能判“没问题”（视觉模型会被页面自身的红色元素、
右侧蓝色标注按钮干扰，实测误报率很高）。唯一可靠的是数像素。

用法：
    python3 check_box.py <图片.png> <x0> <y0> <x1> <y1>

判据：四边占比应接近且不低于 45%（dash=12/gap=4 理论值约 75%，算上抗锯齿取 45% 作下限）。
      某边低于 45% = 那条边没画完；某边接近 0 = 完全缺失。
"""
import sys

from PIL import Image

RED = (220, 38, 38)


def main():
    if len(sys.argv) < 6:
        sys.exit(__doc__)
    img, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
    im = Image.open(img).convert('RGB')
    px = im.load()

    def red(x, y):
        if 0 <= x < im.width and 0 <= y < im.height:
            r, g, b = px[x, y][:3]
            return abs(r - RED[0]) < 70 and abs(g - RED[1]) < 70 and abs(b - RED[2]) < 70
        return False

    def ratio_h(y, xa, xb):
        hit = sum(1 for x in range(xa, xb + 1) for dy in range(-3, 4) if red(x, y + dy))
        return hit / max(1, (xb - xa + 1) * 7)

    def ratio_v(x, ya, yb):
        hit = sum(1 for y in range(ya, yb + 1) for dx in range(-3, 4) if red(x + dx, y))
        return hit / max(1, (yb - ya + 1) * 7)

    top, bot = ratio_h(y0, x0, x1), ratio_h(y1, x0, x1)
    left, right = ratio_v(x0, y0, y1), ratio_v(x1, y0, y1)
    worst = min(top, bot, left, right)

    print('图 %dx%d 框 (%d,%d)-(%d,%d)' % (im.width, im.height, x0, y0, x1, y1))
    print('  上 %.0f%% | 下 %.0f%% | 左 %.0f%% | 右 %.0f%%'
          % (top * 100, bot * 100, left * 100, right * 100))
    if worst < 0.45:
        print('  ✗ 四边不完整：最差一边仅 %.0f%%，重画后再交付' % (worst * 100))
        sys.exit(1)
    print('  ✓ 四边完整')


if __name__ == '__main__':
    main()
