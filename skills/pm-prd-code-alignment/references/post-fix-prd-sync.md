# Post-Fix PRD Sync (Code Fix → PRD Alignment)

When frontend code has been fixed after an audit (new states, buttons, flow changes), the corresponding PRD documents MUST be synchronized. This is a separate step from the audit itself.

## What needs syncing after a code fix

| Code Change | PRD Files to Sync |
|---|---|
| New state (e.g. PENDING_REVIEW) | 主PRD 状态机段落 + Demo_详情页 按钮矩阵 + mermaid流程图 + 字段清单(如有驳回原因) |
| New button (e.g. 审核通过/驳回) | Demo_详情页 按钮矩阵 |
| Flow order change (e.g. 包装扣库存→交运只回传) | 主PRD + context/流程详解 + mermaid流程图 + ManualPage手册 |
| New field (e.g. safetyStock) | 字段清单 + Demo_新增编辑页 + Demo_详情页 + Demo_列表页 |
| Context scope change (e.g. 调拨从二期改一期) | context/03-模块清单 |

## ManualPage.tsx is CODE, not a document

The user manual (`ManualPage.tsx`) is a React component containing mermaid diagrams and operation steps. When the instruction says "只改文档不碰代码", ManualPage.tsx MUST be excluded from that instruction and handled separately with permissive code-editing red-lines.

**Split pattern:**
- Instruction A: Pure docs (PRD/context) — red-line: "禁止修改前端代码"
- Instruction B: ManualPage.tsx only — red-line: "只改ManualPage.tsx，禁止改vite.config"

## State machine walkthrough before implementing

The #1 audit finding is incomplete state machines — developers only implement the happy path (approve) but miss the reverse path (reject → back to editable). Before fixing state machines, do a mental walkthrough:
- Happy path: DRAFT → PENDING_REVIEW → CONFIRMED
- Reject path: PENDING_REVIEW → REJECTED → back to DRAFT (editable)
- Form editability: PENDING_REVIEW = read-only, DRAFT/REJECTED = editable

All three modules (盘点/报损/调拨) suffered from this same gap in today's session.
