#!/usr/bin/env python3
"""Outline or fully dump a .pptx using stdlib only (python-pptx may be absent).

Usage:
    python3 pptx_outline.py deck.pptx           # one line per slide: first text runs
    python3 pptx_outline.py deck.pptx --full    # full text per slide
    python3 pptx_outline.py deck.pptx --gaps    # only slides containing 待补/待确认/TBD/TODO

Why not python-pptx: not always installed; a .pptx is just a zip of
ppt/slides/slideN.xml with text in DrawingML <a:t> elements.

Note: slide numbers can be non-contiguous (deleted slides leave gaps) and they
are NOT guaranteed to equal the printed page numbers in the deck.
"""
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
GAP_MARKERS = ("待补", "待确认", "TBD", "TODO", "占位")


def slides(path):
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)]
    names.sort(key=lambda s: int(re.search(r"slide(\d+)", s).group(1)))
    for n in names:
        num = int(re.search(r"slide(\d+)", n).group(1))
        root = ET.fromstring(z.read(n))
        texts = [t.text.strip() for t in root.iter(A + "t") if t.text and t.text.strip()]
        yield num, texts


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    mode = "outline"
    if "--full" in sys.argv:
        mode = "full"
    elif "--gaps" in sys.argv:
        mode = "gaps"

    try:
        rows = list(slides(path))
    except zipfile.BadZipFile:
        print("NOT A ZIP -> probably a DLP-encrypted wrapper. Check: file <path>; head -c 16 <path> | xxd")
        return 1

    if not rows:
        print("no slides found")
        return 1

    print(f"slides: {len(rows)} (numbering may have gaps: {[n for n, _ in rows]})")
    for num, texts in rows:
        if mode == "gaps":
            hits = [t for t in texts if any(m in t for m in GAP_MARKERS)]
            if hits:
                print(f"\n[slide {num}]")
                for h in hits:
                    print("  -", h[:160])
        elif mode == "full":
            print(f"\n===== slide {num} ({sum(len(t) for t in texts)} chars) =====")
            print("\n".join(texts))
        else:
            print(f"[{num}] {' | '.join(texts[:3])[:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
