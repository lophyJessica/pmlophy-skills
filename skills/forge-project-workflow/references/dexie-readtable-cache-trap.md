# ERP Dexie readTable 缓存陷阱

> 2026-07-18 实战: CRM → ERP 三系统数据串联,连续失败 6 轮才定位到的根因。

## 故障链

```
CRM 写入 forge_erp_db.customers (原生 IndexedDB) ✅
    ↓
ERP readTable('customers') → 从 tableCache 内存 Map 读 ❌
    ↓
ERP 页面永远显示初始 Mock 数据,看不到 CRM 写入的记录
```

## 根因分析

### 根因 1: readTable 缓存陷阱

ERP `src/db/index.ts` 的 `readTable` 函数:

```ts
const tableCache = new Map<DbTableName, unknown[]>();

export function readTable<T>(tableName, initialRows, primaryKey): T[] {
  if (!tableCache.has(tableName)) {
    tableCache.set(tableName, cloneRows(initialRows));  // ① 先设缓存=初始数据
    void hydrateOrSeedTable(tableName, initialRows, primaryKey); // ② void=异步不等待
  }
  return cloneRows(tableCache.get(tableName)); // ③ 永远返回缓存,不读 Dexie
}
```

关键点: `void hydrateOrSeedTable()` —— `void` 关键字让异步水合变成 fire-and-forget。缓存在第①步就被初始 Mock 数据填充了,第②步的 Dexie 数据异步回来时缓存已经返回了。

### 根因 2: DB 名称不匹配 (2026-07-19 追加)

2026-07-19 连续 6 轮调试失败后,Codex 全量诊断发现:**ERP 的 Dexie DB 名是 `qs_inventory_db`,不是 `forge_erp_db`。** 前面所有指令都写错了 DB 名,CRM 一直在往不存在的数据库写数据。

验证方法: 直接读源码 `ERP src/db/index.ts` 中 `constructor()` 的 `super()` 参数。

### 根因 3: Dexie version schema 不匹配

CRM 用 `new Dexie('qs_inventory_db')` 不定义 stores 时,若 ERP 已创建了 v1-v6 的 schema,CRM 的 Dexie 不会自动继承——必须定义**完全相同**的 version().stores()。

**正确做法 (2026-07-19 验证通过):** 复制 ERP 的 v1-v6 全部 stores 定义到 CRM 的 erpSync.ts,12 张表不增不减。

## 修复方案

### 方案 A: 页面挂载时强制刷新缓存

在 `db/index.ts` 添加:
```ts
export async function refreshCacheFromDb(tableName: DbTableName) {
  tableCache.delete(tableName);
  await hydrateOrSeedTable(tableName, [], 'code');
}
```

在 `CustomerList.tsx` 的 `useEffect` 中调用:
```ts
import { refreshCacheFromDb } from '../db/index';
useEffect(() => { refreshCacheFromDb('customers'); }, []);
```

### 方案 B: baseDataApi 绕过 readTable 直读 Dexie

```ts
// 不用 readTable,直接用 db.table.toArray()
import { db } from '../db/index';
getCustomers(): Promise<BaseCustomer[]> {
  return db.customers.toArray();
}
```

## 其他 Dexie 跨系统坑

1. **不要定义 version().stores()** — ERP 的 DB 有 12 张表,CRM 只定义 4 张会导致 schema 不匹配
2. **baseDataApi 改造时保持函数签名不变** — 页面零改动
3. **验证方法**: DevTools → Application → IndexedDB → forge_erp_db → customers
