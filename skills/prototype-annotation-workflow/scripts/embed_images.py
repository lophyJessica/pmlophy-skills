#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评审PRD 图片内嵌发布版生成脚本。
把 md 里的图片相对引用替换成 base64 data:URI，生成"自包含"发布版，
发到语雀/Confluence/邮件等任何平台图都不会断（本类文档交付前的标准动作）。

背景: Cursor 的 md 预览不支持图片点开放大, GitHub 点图要跳转, 都不适合发给外部人;
语雀/Confluence 支持图片放大。跨平台交付 = md 源(仓库维护) + 本脚本生成 base64 发布版。

用法:
  python3 embed_images.py <评审PRD.md> [--img-dir <目录>] [--output <输出.md>]

默认: --img-dir = md 所在目录的 images/ 子目录; --output = <原名>-发布版.md
规则: 只处理 md 里的 ![alt](./images/xxx.png) 相对引用; 找不到图报错并退出(避免发布版缺图)。
"""
import argparse, base64, os, re, sys

IMG_RE = re.compile(r'!\[([^\]]*)\]\((\./images/[^)]+)\)')

def embed(md_path, img_dir, out_path):
    with open(md_path, encoding='utf-8') as f:
        text = f.read()
    missing, replaced = [], [0]

    def repl(m):
        alt, rel = m.group(1), m.group(2)
        img = os.path.join(img_dir, os.path.basename(rel))
        if not os.path.isfile(img):
            missing.append(rel)
            return m.group(0)
        with open(img, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
        ext = os.path.splitext(img)[1].lstrip('.').lower() or 'png'
        replaced[0] += 1
        return f'![{alt}](data:image/{ext};base64,{b64})'

    new_text = IMG_RE.sub(repl, text)
    if missing:
        print(f'缺失 {len(missing)} 张图，未内嵌: {missing}', file=sys.stderr)
        sys.exit(1)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print(f'已内嵌 {replaced[0]} 张图; 源 {md_path} ({os.path.getsize(md_path)/1024:.0f}K) -> 发布版 {out_path} ({os.path.getsize(out_path)/1024:.0f}K)')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('md')
    ap.add_argument('--img-dir', default=None)
    ap.add_argument('--output', default=None)
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.md))
    img_dir = a.img_dir or os.path.join(base, 'images')
    out = a.output or os.path.splitext(a.md)[0] + '-发布版.md'
    embed(a.md, img_dir, out)