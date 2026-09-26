#!/usr/bin/env python3
"""把 markdown 里的相对图片引用替换成 base64 data:URI，生成自包含发布版。
用法: python3 embed_images.py 评审PRD.md --output 评审PRD-发布版.md
发布版导入语雀/Confluence 图片路径不断、可放大。仓库维护仍用引用版(md+images/)。
"""
import argparse, base64, os, re, sys

def embed(md_path, out_path):
    with open(md_path, encoding="utf-8") as f:
        md = f.read()
    base = os.path.dirname(os.path.abspath(md_path))

    def repl(m):
        alt, path = m.group(1), m.group(2)
        full = os.path.join(base, path)
        if not os.path.isfile(full):
            print(f"[跳过] 缺失图片: {path}", file=sys.stderr)
            return m.group(0)
        ext = os.path.splitext(full)[1].lstrip(".").lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp"}.get(ext, "application/octet-stream")
        b64 = base64.b64encode(open(full, "rb").read()).decode("ascii")
        return f"![{alt}](data:{mime};base64,{b64})"

    new = re.sub(r"!\[([^\]]*)\]\(\s*\.?/?images/([^)\s]+)\)", repl, md)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"源: {md_path} ({os.path.getsize(md_path)} B)")
    print(f"发布版: {out_path} ({os.path.getsize(out_path)//1024} KB)")
    replaced = new.count("base64,")
    print(f"内嵌图片: {replaced} 张; 残留 relative images/: {new.count('images/')}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("md")
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    embed(a.md, a.output)
