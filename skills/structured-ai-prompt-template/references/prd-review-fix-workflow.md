# PRD/Mock 走查返修 · A2A 执行闭环

Validated on forge-wms 走查返修 (2026-07-08). The user hands a **terse 走查 checklist** (🔴必修/🟠中/🟡低, e.g. "货位命名统一 / Mermaid \n→<br/> / Mock 层级引用链对齐"). Hermes turns each item into a **五段式 Codex/反重力 指令**, the user runs + pushes, Hermes does an **independent 全面检查**. Hermes writes prompts; the IDE agent executes; Hermes verifies.

## The loop
1. **Ground before writing.** For each item, READ the actual files to get file path + line numbers + current values. A 五段式 指令 精准到行号 is what makes the agent fast and correct — never write a fix 指令 from the terse checklist alone.
2. **Verify WHERE the defect lives — it often flips the fix.** "货位命名统一 (snake_case→camelCase)" looked like a code change, but `types/baseData.ts` was ALREADY camelCase — the real fix was DOC-side (`货位字段清单.md` lagging). Check code vs doc vs mock before deciding the 指令's target; writing "改代码" when code is already correct just confuses the agent.
3. **Anchor to an in-repo SSOT / correct sibling — never an invented standard.** For 货位命名, `库区字段清单.md` was already in the target style → tell the agent "照隔壁库区的口径". For a systemic SKU-coding split, the SSOT was `商品档案字段清单.md` + the front-end seed `db/index.ts` (both used `SKU001` 口径) — proving BOTH divergent mock sets (`SKU-A100` and `SKU10086`) were wrong. Always find the authoritative anchor (the SSOT doc, or the actual code/app seed) and align everything to it. The user reacts well to "对齐代码/SSOT" and dislikes pulled-from-thin-air standards.
4. **File-isolation governs parallelism.** Two 指令 that touch ANY common file CANNOT run in parallel (merge conflict / overwrite). Diff their file lists. If they overlap (⑤a edited `交运单_用例数据推演.md`; ④'s audit scope also included it) → serialize, or better MERGE them into one 指令. One item is often a subset of another (a "无源引用" is exactly what an "引用链审计" would catch) → merge to save the user a review pass. When the user asks "X 和 Y 能并行吗", answer by checking file overlap, not by guessing.
5. **Route by tool strength — but 五段式 is tool-agnostic.** Codex+GPT5.5 = 文档/mock/重构 audits; 反重力+Gemini = front-end page generation. When Codex is down and you fall back to 反重力 for a DOC task, ADD hardening 红线 (below).
6. **Verify, don't trust the agent's self-report.** After the user runs + pushes, `git pull` and INDEPENDENTLY confirm each fix: grep residual (mermaid `\n`→0, snake_case→0), check the specific conflict is gone, check cross-refs now trace. The 全面检查 is where you catch what the agent missed — e.g. a bare-pipe defect hiding in a `字段清单` file the earlier read had skipped.

## Codex → 反重力 fallback hardening
反重力's instinct is "generate front-end pages, fast, eager to edit." For a pure DOC/mock audit its default red-lines aren't enough. Replace the 红线禁止 block with:
```
红线禁止:
- 【本次是纯文档审计，不是做页面】不许生成/改动任何前端页面或代码；
  front-prototype/ 下的 .tsx/.ts/db/api 一行不许碰，只读改 prd-docs/ 下的 .md。
- 【别一把梭】必须先出差异报告表；系统性问题（如 SKU 主数据统一）只报告、不改；
  拿不准来源的引用标"待确认"。
- 不动已修完的成果；单号遵 context/09；不改业务判定与公式。
- 路径一律用项目内相对路径。
```

## Systemic vs clear-fix separation (respects 人脑层防过载)
In an audit 指令, tell the agent to DIRECTLY fix unambiguous breaks (a downstream mock referencing a non-existent upstream number) but to ONLY REPORT systemic decisions (whole-module SKU recoding, module-wide naming scheme) for human sign-off — output a 差异报告表 + 待决策清单. This keeps the diff reviewable and caps the user's review load. 反重力 correctly left the SKU systemic issue for decision when told to.

## Delivery shape
- Deliver 返修 指令 **inline** (copy-paste into the IDE agent). The `链名-NN-单据名_填充指令.md` file convention is for multi-单据 PRD *generation*, not small返修.
- Deliver 🔴 first / merge overlapping items; don't dump all items at once (review overload).
- Trivial 1-line doc fixes: offer to just do it yourself (VPS edit + let user pull), but a VPS→GitHub push needs auth the VPS lacks — see `vps-administration` "Git Sync" section; prefer having the user push from the Mac or SSH-in.
