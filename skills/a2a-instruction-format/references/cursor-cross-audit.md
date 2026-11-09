# Cursor 交叉审计：反重力出码后必做

> 2026-07-30 建立：反重力全量 antd 迁移后,Cursor 审计发现 5 项 P0/P1 问题。

## 背景

反重力(Gemini)生成速度快但毛糙——删一行能重构全路由层、梭哈后留 5-12 套重复路由树。同一个 AI 不会说自己错了,换一个(Cursor Agent)从零审计能发现前者漏掉的问题。

## 审计指令模板

在 Cursor Agent 模式(Cmd+I,选 Agent):

```
@codebase 审计以下5项，只读不改:

1. 搜"SKU00" — 列出位置，判断是商品编码还是变量名
2. 搜"BrowserRouter|createBrowserRouter" — 列出所有路由定义位置
3. 搜"SUPPLIER.*navigate|SUPPLIER.*to=" — 列出角色跳转位置
4. 检查 src/pages/ 中所有 .tsx 是否都在路由中注册
5. 列出所有 mock 数据文件，确认数据源唯一性

每项输出: 文件:行号 → 内容 → 严重度(P0/P1/P2) → 建议
```

## 真实案例：forge-erp antd 全量迁移审计结果

### P0 — 阻断性

| 问题 | 细节 |
|------|------|
| 供应商编码三套并存 | `SUP001`(Login预设) vs `SUP001`(Import兜底) vs `VEND001`(MOCK_SUPPLIERS)。报价匹配全挂 |
| 主数据双份定义 | `purchaseOrder.MOCK_*` vs `baseData.getInitial*()`,商品数量不一致(7 vs 6,缺SP-007) |

### P1 — 高风险

| 问题 | 细节 |
|------|------|
| 无角色路由守卫 | ProtectedRoute 只校验登录,不校验角色。供应商访问 `/purchase/orders` 成功 |
| 合同/通知走 localStorage | 与 Dexie(qs_inventory_db) 数据分裂 |

### P2 — 低风险

| 问题 | 细节 |
|------|------|
| App.tsx 内 `Layout` 组件疑似死代码 | RouteWrapper 实际用 ForgeLayout,此 Layout 从 v1 遗留 |
| SKU001 实际不存在 | 审计确认前端全用 SP-001~007,与 PRD 的 SKU 术语仅文档层漂移 |

## 发现的非问题（避免了无效改动）

- **SKU001 根本不存在于代码中**: 前端 mock 数据一直用 SP-001~007,反重力之前就用了 SP
- **角色跳转只在 Login.tsx:34 一处**: 没有多处重复,之前误判为多处跳转
- **67 个页面全在路由中注册**: 无漏注册,覆盖率 100%

## 使用流程

```
反重力(快速生成) → Cursor Agent(只读审计) → 按P0→P1→P2顺序修复 → npm run build → 发 dist
```
