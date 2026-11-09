# 跨系统 Debug 铁律

> 来源:CRM→ERP 数据同步 6 轮失败后 Codex 一局修复 (2026-07-18)

## 教训

CRM 转客户后 ERP 客户列表看不到数据。Hermes 手工 patch 了 6 轮:
- 加 erpSync.ts
- 改 Dexie schema
- 绕过版本冲突
- 改成原生 IndexedDB
- 修复 readTable 缓存
- 加 refreshCacheFromDb

每一轮都是单点猜测,没做全量诊断。最终 Codex 一次读了两边的完整 db/index.ts + erpSync.ts,发现根因:**CRM 的 DB 名 `forge_erp_db` 是错的,ERP 实际叫 `qs_inventory_db`。**

## 铁律

同一 bug 修复 **超过 3 轮仍未解决** → 停止手工 patch,交给 Codex 做全量诊断:

1. 读两边的完整代码
2. 对比 DB 名/表名/主键/字段/类型
3. 一次性定位根因
4. 一次性修复

手工 patch 循环的代价:浪费 token + 浪费时间 + 用户失去耐心。
