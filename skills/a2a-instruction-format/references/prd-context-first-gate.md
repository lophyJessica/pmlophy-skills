# PRD Context-First Gate

> 2026-07-29 forge-erp 供应商报价模块 PRD 定位纠错实战记录

## 教训

**PRD 定位错误时，不可直接在 PRD 里修——必须先回溯 context，再重写 PRD。**

## 案例：供应商报价 PRD 定位错误

| 阶段 | 错误 | 修正 |
|------|------|------|
| 初版 PRD | 定位为"采购员侧辅助记录单据"，有 BJ 单号前缀，状态"草稿→已报价" | — |
| context/04 | 写成了"供应商报价单 (BJ)"，In Scope 是采购员录入 | — |
| context/05 | 新增了 BJ 和 INQ 单号前缀 | — |
| 实际需求 | 供应商侧报价工作台，挂 rfqId，不产生独立单号，状态"待报价→已报价" | — |

## 修正流程（正确做法）

```
1. 用户指出 PRD 定位错误
2. ↓ 改 context/04 → "供应商报价工作台（供应商侧）"，删除 BJ 前缀描述
3. ↓ 改 context/05 → 删除 BJ 和 INQ 编码前缀
4. ↓ 发文件给用户覆盖 Mac 本地 → 用户确认
5. ↓ 重写 PRD 套件（主PRD + 字段清单 + Demo列表页 + Demo报价操作页）
6. ↓ 删除旧目录 prd-docs/采购管理/供应商报价单/
7. ↓ 同步 flowchart.md（系统交互流程图）
8. ↓ 走查通过 → 出前端指令
```

## 错误做法（不可行）

```
用户指出错误 → 直接改 PRD 文件（字段/状态/编码）
→ context 与 PRD 不一致 → AGENTS.md 铁律："改规则须回溯 context"
```

## VPS 操作铁律

**在 VPS 上修改 context/PRD 前，必须先 `git stash && git pull`。**
用户 Mac 是源码权威源，VPS 侧 pull+审计后修改，改完发文件给用户覆盖。

## 关联规则

- AGENTS.md: "context/ > templates/ > prd-docs/，改规则须回溯 context"
- forge-project-workflow §5: "字段问题只改字段清单，规则问题只改主PRD"
- context 文件是最高权威源，PRD 是生成物
