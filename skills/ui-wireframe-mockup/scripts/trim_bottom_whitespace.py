#!/usr/bin/env python3
"""裁掉截图底部的空白留白，并报告内容是否可能被截断。

用法: python3 trim_bottom_whitespace.py shot.png [more.png ...]

判定: 从底部向上扫第一条「非空行」（该行采样里超过 2 个像素 < 240 即算非空），
      裁到「内容底 + pad」。若「底部原留白」< 80px（2 倍图）说明内容可能被切，
      把 chrome 的 --window-size 高度调大重截，不要直接发图。
"""
import sys

from PIL import Image


def trim(path, scale=2, pad_css=36, step=4):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    px = im.convert('L').load()
    bottom = h
    for y in range(h - 1, -1, -1):
        dark = 0
        for x in range(0, w, step):
            if px[x, y] < 240:
                dark += 1
                if dark > 2:
                    break
        if dark > 2:
            bottom = y
            break
    cut = min(h, bottom + pad_css * scale)
    im.crop((0, 0, w, cut)).save(path)
    slack = h - bottom
    flag = '  <-- 可能被截断，调高窗口重截' if slack < pad_css * scale else ''
    print(f'{path}: {w}x{h} -> {w}x{cut}  (底部原留白 {slack}px){flag}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for p in sys.argv[1:]:
        trim(p)
