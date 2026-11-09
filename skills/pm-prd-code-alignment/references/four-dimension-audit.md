# 四维对齐审计模板

本模板用于对 forge-erp / forge-wms 等 PRD 驱动的前端项目做全面交叉审计。
适用于 AI Agent（Codex 做审计分析，反重力做修改执行）的场景。

## 四个审计维度

| 维度 | 检查什么 | 源文件 | 目标文件 |
|------|---------|--------|---------|
| Context 对齐 | 术语是否统一、单号前缀是否登记、边界约束是否同步 | context/ | prd-docs/ |
| PRD 与原型对齐 | 筛选项/表格列/按钮/字段状态是否一致 | prd-docs/ Demo PRD | front-prototype/src/pages/ |
| 流程对齐 | 状态机是否有死状态、上下游单据状态引用是否存在 | context/流程 + PRD 状态机 | front-prototype/src/pages/ |
| 功能清单对齐 | context 标 In Scope 的模块是否都有 PRD 和页面 | context/03 模块清单 | prd-docs/ + pages/ |

## 输出格式

P0/P1/P2 分级，每条：`严重级 | 维度 | 项目 | 问题描述 | 源文件:行号 | 目标文件:行号 | 修复方向`

- P0: PRD 有但页面缺失、context 不一致、单号前缀漂移
- P1: 字段/按钮不一致但功能可用、命名别名未统一
- P2: 文案微差、派生数据完整性、未来期标注

## 审计指令模板（给 Codex）

```plaintext
Context:
{项目名} 前端项目，经多轮迭代后需做四维对齐审计。

Request:
逐文件交叉对比，找出不一致项：
1. Context对齐：context/ vs PRD术语/单号前缀/边界约束
2. PRD与原型对齐：prd-docs/ Demo PRD vs front-prototype/src/pages/ tsx（筛选项/列/按钮/字段状态）
3. 流程对齐：context/流程 vs PRD状态机（死状态/上下游状态引用）
4. 功能清单对齐：context/03 vs prd-docs/实际目录 vs pages/实际页面

Output format:
P0/P1/P2 分级清单，每条：严重级|维度|问题|源文件|目标文件|修复方向

红线：只审计不改代码，禁止commit/push
```

## Agent 分工

| Agent | 擅长 | 用在哪 |
|-------|------|--------|
| Codex | 只读审计、从零生成新文件、文档分析 | 四维审计、PRD 生成、手册更新 |
| 反重力 | 修改已有代码、跨文件联动、精确控制 | 页面修复、路由调整、样式修改 |

**Codex 做审计不改代码，反重力接审计结果执行修复。两个项目必须拆成独立 session 分别喂指令——Codex 在 wms 目录喂 erp 指令会跑去改别处文件。**

## VPS 部署部署路径（方案 A）

vite base 必须对齐 nginx alias：
- ERP: `base: '/project/forge-erp/'` → nginx `alias /var/www/pmlophy.com/project/forge-erp/`
- WMS: `base: '/project/forge-wms/'` → nginx `alias /var/www/pmlophy.com/project/forge-wms/`

HashRouter 用 `#/` 处理路由，不依赖 URL 路径，改 base 不需改路由代码。

部署 pitfall：反重力编译打包时 dist 可能嵌套在子目录（如 `wms-dist/dist/`）而非根级 `dist/`，解压后需先 `find` index.html 定位实际路径再移动。
