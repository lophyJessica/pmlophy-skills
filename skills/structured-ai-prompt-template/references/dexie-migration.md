# Dexie.js 迁移模式（localStorage → IndexedDB）

> 适用：进销存 ERP、WMS 两个项目的 localStorage 全量迁移

## 改写规则

```
localStorage.getItem(KEY)               → await db.tableName.toArray()
localStorage.setItem(KEY, json)         → await db.tableName.bulkPut(list)
JSON.parse(localStorage.getItem(KEY))   → await db.tableName.toArray()
if(!localStorage.getItem(KEY)) { init } → if(await db.tableName.count() === 0) { init }
```

## 标准数据库模板

```typescript
// src/db/index.ts
import Dexie from 'dexie';

class AppDb extends Dexie {
  purchaseOrders!: Dexie.Table<PurchaseOrder, string>;
  stockInRecords!: Dexie.Table<StockInRecord, string>;
  // ... 其他表

  constructor() {
    super('app_db');
    this.version(1).stores({
      purchaseOrders: 'id',
      stockInRecords: 'id',
      // 主键用单据号或编码
    });
  }
}

export const db = new AppDb();
```

## 常见坑

1. **Codex 改完代码忘装包**：`npm install dexie` 需要单独提醒或手动执行
2. **包导入路径**：所有 `api/*.ts` 从 `../db` 导入 `db` 实例
3. **保留 Mock 初始化**：`db.tableName.count() === 0` 时仍执行种子数据填充
4. **API 签名不变**：只改存储层，不改函数签名和返回值结构
