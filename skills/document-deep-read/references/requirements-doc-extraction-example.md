# Example: Deep Extraction of a Chinese Requirements Spec

Real session: extracting Chapter 3 from a 23MB hospital drug inventory optimization
requirements document (对外分享版).

## Document Profile

- **File**: `基于AI及高质量数据的医院药品库存优化与智能补货平台建设项目_建设需求说明书_V8_对外分享版.docx`
- **Size**: 23MB, 9278 lines after auto-extraction
- **Structure**: 19 chapters, 171 tables, 1132 non-empty paragraphs
- **Language**: Chinese
- **Type**: 对外分享版 (sanitized — vendor names and participant details removed)

## What Went Wrong

1. **search_files returned 0 for terms clearly in the document** — Terms like
   "访谈", "泽信", "调研材料", "药师.*工作" all returned 0 matches, even though
   `read_file` showed them in the text. This is the core trigger for the
   dual-approach pattern.

2. **python-docx paragraph iteration only showed headings** — The body content
   was in a different XML structure. `read_file` auto-extraction had the body
   text but python-docx paragraph iteration initially only returned TOC entries.
   Solution: use `read_file` for body text, python-docx for targeted table/search.

3. **Vendor names absent** — NJGL/泽信 were not in the document because this
   was an 对外分享版. The appendix explicitly stated interview details are in
   a separate archive.

## What Worked

1. **read_file for bulk chapter location** — Found Chapter 3 at lines 372-407
   in one call with limit=500.

2. **execute_code + read_file loop for full-text cross-reference** — Batched
   reads of 2000-line chunks to build a complete searchable text, then Python
   regex to find all mentions of hospital names, department types, etc.

3. **python-docx for tables** — 171 tables in the document, many containing
   structured requirements (需求规格表). Parsed these for the data layer.

## Extraction Output Structure

For requirements documents, structure the extraction around:
1. Interview/survey participant inventory (角色/科室)
2. Per-site findings with original quotes
3. Existing process descriptions
4. Pain points with verbatim evidence
5. Pharmacist workflow descriptions
6. Existing system problem inventory
7. Root cause analysis from the PM

Always include line-numbered `原文引用` blocks so readers can verify.
When information is absent (like vendor names in sanitized docs), state it
clearly rather than continuing to search.
