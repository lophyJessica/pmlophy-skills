# 三系统数据同步方案 (ERP/CRM/WMS)

> 2026-07-18 CRM 项目实战记录

## 最终状态

| 系统 | 存储 | 数据库名 | 互通 |
|------|------|---------|:--:|
| ERP | Dexie | `forge_erp_db` (类名 QsInventoryDb) | ✅ |
| CRM | Dexie | `forge_crm` (类名 ForgeCrmDatabase) | ✅ |
| WMS | Dexie | (WmsDatabase) | ✅ |

## 关键坑点

1. **ERP 原来是内存态 baseDataApi** — 升级到 Dexie 后才能被 CRM/WMS 读取。升级时保持函数签名不变,现有页面无需修改。
2. **ERP 导出变量名是 `db` 不是 `erpDb`** — CRM 引用时要确认实际导出名。
3. **CRM 转客户同步失败** — handleConvertToCustomer 只更新了 CRM 本地 Dexie,未调用 erpSync 写入 ERP。需在转换逻辑中显式调用 `addCustomerToErp()`。
4. **跨系统 IndexedDB 访问** — 同域名 `pmlophy.com` 下可直接打开对方 DB,无需 API。

## 同步模式

```
CRM 转客户 → CRM 更新本地 lead.status=CONVERTED
           → erpSync.addCustomerToErp() 写入 forge_erp_db.customers
           → ERP 刷新可看到新客户

ERP 创建客户 → forge_erp_db.customers.add()
            → CRM CustomerList 用 useLiveQuery 实时读取

未来: WMS 出入库 → ERP 可读取 WMS 的 Dexie 库存数据
```

## 调试步骤

1. 确认 ERP 使用 Dexie: `grep -rn "Dexie" src/db/`
2. 确认 CRM 有 erpSync.ts: `cat src/api/erpSync.ts`
3. 确认转客户逻辑调用了 erpSync: `grep "erpSync\|addCustomer" LeadDetail.tsx`
4. 浏览器 DevTools → Application → IndexedDB → 检查 forge_erp_db.customers 表是否有数据
