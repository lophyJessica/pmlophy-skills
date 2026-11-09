# 三系统 Dexie 数据串联方案

> 2026-07-18 CRM/ERP Dexie 数据互通实战全记录

## 技术前提

- 三系统部署在同一域名 `pmlophy.com`
- IndexedDB 按域名隔离,同域名可互相访问对方数据库
- ERP 的 DB: `forge_erp_db` (12张表, v6)
- CRM 的 DB: `forge_crm` (自有)

## 踩过的全部坑

### 坑1: ERP 用内存态 baseDataApi → CRM 读不到
修复: ERP 创建 `db/index.ts`,改造 `api/baseData.ts` 内部用 Dexie CRUD 替代内存。**函数签名保持不变,页面零改动。**

### 坑2: Dexie 版本 schema 冲突(关键)
CRM 侧定义 `version(1).stores({...})` 只4张表,ERP v1 有12张 → schema 不匹配 → 打开失败。
修复: 用原生 IndexedDB API,不定义 schema:
```ts
const req = indexedDB.open('forge_erp_db');
req.onsuccess = () => req.result.transaction('customers','readwrite').objectStore('customers').add(c);
```

### 坑3: erpSync.ts 多次没被创建
Codex 多次跳过了创建文件的指令 → 源码文件根本没出现。

### 坑4: dist 命名混淆
用户发了 crm-dist 但命名为 erp-dist.zip → 覆盖了 ERP。恢复:用缓存的上一个正确 dist。

## 验证方法\nDevTools → Application → IndexedDB → `forge_erp_db` → `customers` → CRM 和 ERP 页面数据一致。\n\n### 坑5: ERP 的 readTable 含内存缓存(最后修复)\nCRM 写入 Dexie 成功,但 ERP 仍看不到 → 因为 `readTable` 从 `tableCache`(内存 Map)读取,不是从 Dexie 读取。\n修复: baseDataApi 的 getCustomers/getSuppliers 等改为 `db.xxx.toArray()` 直读 Dexie,绕开 readTable 缓存。
