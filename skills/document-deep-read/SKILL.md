---
name: document-deep-read
description: "Deep-read large documents (.docx, .xlsx, .pdf) — find, extract, and cross-reference structured content when simple grep fails."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Documents, DOCX, XLSX, Extraction, Analysis]
    related_skills: [docx, ocr-and-documents, xlsx]
---

# Document Deep Read

When you need to deeply extract structured content from large office documents
— requirements specs, technical reports, long proposals — where finding
specific sections and cross-referencing findings is critical.

**This skill covers the extraction/analysis path.** For document creation/editing,
see `docx`, `xlsx`, or `pdf`.

## The Core Pattern

`read_file` auto-extracts .docx/.xlsx to readable text with line numbers. This
is your primary tool for bulk reading and section discovery. But `search_files`
(ripgrep) can return **zero results** on auto-extracted text due to extraction
artifacts — the same terms visible in `read_file` output may not match.

When `search_files` fails, fall back to the native parser for that format via
`execute_code`.

### .docx: read_file → python-docx

```
Phase 1: read_file for bulk discovery and chapter location
Phase 2: python-docx for targeted search (paragraphs + tables)
Phase 3: execute_code to cross-reference and batch-analyze
```

**Phase 1 — Discovery with read_file:**
```python
from hermes_tools import read_file

# Find chapter boundaries
result = read_file(path, offset=1, limit=500)
# Output: "372|第3章 行业背景、业务调研与痛点分析"
```

`read_file` on .docx auto-extracts:
- Paragraph text with line numbers
- Table of contents entries
- Table cell content (flattened inline)

**Phase 2 — Targeted search with python-docx:**
When `search_files` returns 0 for terms visible in read_file output:

```python
from docx import Document

doc = Document(path)

# Search paragraphs
for i, p in enumerate(doc.paragraphs):
    if 'target_term' in p.text:
        print(f"P{i}: {p.text[:200]}")

# Search tables — critical for Chinese requirements docs!
for i, table in enumerate(doc.tables):
    for j, row in enumerate(table.rows):
        row_text = ' | '.join(cell.text for cell in row.cells)
        if 'target_term' in row_text:
            print(f"T{i}R{j}: {row_text[:300]}")
```

**Phase 3 — Cross-reference in execute_code:**
```python
from hermes_tools import read_file

# Batch-read full document
all_text = ""
offset = 1
while True:
    result = read_file(path, offset=offset, limit=2000)
    all_text += result["content"]
    total = result.get("total_lines", 0)
    if offset + 2000 > total:
        break
    offset += 2000

# Search for multiple terms
lines = all_text.split('\n')
terms = ['鼓楼', '急诊', '静配', '痛点']
for t in terms:
    matches = [l for l in lines if t in l]
    print(f"'{t}': {len(matches)} matches")
    for m in matches[:3]:
        print(f"  {m.strip()[:200]}")
```

### .pptx: no `read_file` support → zipfile + DrawingML

`read_file` does **not** auto-extract .pptx, and `python-pptx` is often absent. The deck is just a
zip: each slide is `ppt/slides/slideN.xml`, and every text run is an `<a:t>` element in the
DrawingML namespace (`.../drawingml/2006/main`). Read it with stdlib only:

```python
import zipfile, re
from xml.etree import ElementTree as ET
ns = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
z = zipfile.ZipFile(path)
slides = [n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$', n)]
slides.sort(key=lambda s: int(re.search(r'slide(\d+)', s).group(1)))
for n in slides:
    texts = [t.text.strip() for t in ET.fromstring(z.read(n)).iter(ns + 't') if t.text and t.text.strip()]
    print(n, ' | '.join(texts[:3])[:90])   # title line per slide = outline
```

- **Slide numbers are not contiguous** — deleted/reordered slides leave gaps (`1,4,5,9,10,14,25 …`).
  Sort by the integer, then address pages by the **real** slide number; never assume `1..N` or
  `len(slides)` equals the last page number.
- `run scripts/pptx_outline.py <deck.pptx> [--full]` does this for you: outline by default,
  full per-slide text with `--full`.
- Want to know what the deck **promises but hasn't filled in**? Grep the extracted text for
  placeholder markers (`待补`, `待确认`, `TBD`, `TODO`) and list them per slide — that is the fastest
  read on a draft's real gaps, and it stays useful when the user asks "差在哪".

### .xlsx: read_file → openpyxl/pandas

Same pattern. `read_file` auto-extracts .xlsx to text tables. When search_files
fails or you need structured cell access:

```python
import openpyxl
wb = openpyxl.load_workbook(path)
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for row in ws.iter_rows(values_only=True):
        # process
```

## Common Pitfalls

### Check the file header before parsing — corporate DLP wrappers masquerade as PDF/Office
A file that ends in `.pdf`/`.pptx` can be a **DLP-encrypted shell** rather than the format it claims.
Symptoms are misleading library errors: pymupdf → `FzErrorFormat: no objects found`, `read_file` →
`UnsupportedError`, zipfile on a .pptx → `File is not a zip file`. Do **not** start swapping parsers;
check the magic bytes first:

```bash
file <doc>                 # often "data"
head -c 16 <doc> | xxd     # %TSD-Header-###%  => DLP wrapper (天锐绿盾 class)
```

An encrypted wrapper only opens inside the company's own client. Say so plainly, and pivot to a
channel that works (screenshots, an exported plain copy, a link) instead of retrying extraction —
the failure is not in the parser and not in the file being corrupt.

### "对外分享版" / sanitized documents
Documents labeled as "对外分享版" or "脱敏版" have vendor names, person names,
dates, and specific system identifiers removed. The document will state this:

> "具体资料清单、版本、日期和责任人由项目资料档案统一管理，不在正文中逐项展开。"

This is NOT a search failure — the info is genuinely absent. Report it clearly.

### Tables are separate from paragraphs
In Chinese requirements documents especially, structured content (需求矩阵,
规格表) lives in tables. `python-docx` tables and paragraphs are separate
collections — always search both.

### Identify markdown tables by HEADER keywords, not heading text
When parsing a big markdown doc for a specific kind of table, a table is
identified by its header-column names (e.g. `字段名称`, `什么情况下`+`结果`),
NOT by the section heading above it. Section headings are reuse-prone short
labels — `6.1 商机列表页` and `5.1 创建与引用` carry no literal "字段清单"/"业务规则"
keyword, yet contain those tables. Match on `header row` + a structural regex
(section-number `^\d+\.\d+`), never `.startswith('五、')` style prose matches.
Column-name aliases also differ between source and derived docs (`必填性` vs
`是否必填`) — read both, with a fallback shortcut. This is exactly where a
first parse pass silently returns 0 rows and looks green.

### Over-simplified labels vs authoritative detail in cross-doc compare
Comparing a derived doc (summary) to its authority (detailed): treat "source
is a substring / a more detailed superset" as consistent; a renamed field
(`客户名称` vs `关联客户`) and a reworded rule are "needs human confirm", not
definitive diffs. Only a truly missing field/rule or a real requiredness change
is a definite diff. Otherwise every summary-vs-detailed pair flags as different
and the compare is noise.

### 用户说“发你了”但你没看到文件 → 先查缓存目录，别断言通道坏了

用户发来的文件落在 `/root/.hermes/cache/documents/`，图片在 `cache/images/`。在说“文件没收到 /
飞书收不到文件”之前，先跑 `ls -lt /root/.hermes/cache/documents/ | head`。

**历史经验不能当作当前事实。** 上次没收到的经验不代表这次收不到；用一条过时的结论去否定眼前
实际存在的文件，比不知道更糟——用户得先跟你辩解一个你一条命令就能查到的事实（“别乱扯飞书收不到，行吗”）。
同理适用于任何“XX 不能用”的历史结论：先看本次运行时的实际状态。

### Large files (20MB+)
Documents >20MB with 9000+ lines need multiple `read_file` calls. Batch them
in `execute_code` to avoid excessive tool call overhead.

## References

- `references/requirements-doc-extraction-example.md` — real-session example of
  deep-extracting Chapter 3 from a 23MB Chinese hospital requirements spec (对外分享版),
  with pitfalls encountered and output structure template.

## When Not to Use

- Simple "find a phrase in a docx" — just use `read_file` + eyeball, or `search_files`
- Document creation/editing — see `docx`, `xlsx`, `pdf` skills
- The document is already open in a browser — use browser tools
