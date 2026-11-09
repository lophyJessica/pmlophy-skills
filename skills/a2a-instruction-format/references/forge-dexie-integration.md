# Forge 三系统 Dexie 集成模式

## 架构

三个系统部署在同一域名 pmlophy.com 下，共享 IndexedDB：
- ERP: Dexie DB名 `qs_inventory_db`, 实例变量 `db`, 类 `QsInventoryDb`, v1-v6 共6个版本
- WMS: Dexie DB名待确认, 实例待确认
- CRM: 独立 Dexie DB `forge_crm`, 通过 `erpSync.ts` 读写 ERP 的 DB

## 关键发现 (CRM↔ERP 6轮调试后 Codex 一局修复)

**根因**: CRM 的 erpSync.ts 中 DB 名写成了 `forge_erp_db`, 但 ERP 实际 DB 名是 `qs_inventory_db`。

**为什么会这样**: Hermes 多次给指令时猜测 DB 名, 没有先读源码确认。Codex 全量读了 ERP 的 `db/index.ts` 发现真实 DB 名, 一次性修复。

**教训**: 跨系统集成任务, 必须让 Agent 先"读源码→确认精确的 DB 名/表名/主键/类型", 再写代码。不能凭记忆或猜测。

## 集成 Checklist

| 检查项 | 怎么验 |
|--------|--------|
| DB 名一致 | 两边 `new Dexie('xxx')` 字符串完全一致 |
| version.stores 一致 | CRM 侧必须复制 ERP v1-v6 全部 stores 定义 |
| 主键类型一致 | ERP 用 `id: string` (WithId<T>), CRM 也必须构造 id 字段 |
| 字段结构一致 | ERP BaseCustomer 的所有字段 CRM 都传入 |
| 写入验证 | CRM 转客户后浏览器 DevTools → Application → IndexedDB → qs_inventory_db → customers 表确认有数据 |
