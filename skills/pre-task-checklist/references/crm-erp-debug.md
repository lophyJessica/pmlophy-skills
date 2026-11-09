# CRM→ERP 数据同步调试记录

## 问题

CRM 转客户后 ERP 客户列表看不到数据。

## 调试历程(6轮失败)

| 轮次 | 尝试 | 失败原因 |
|:--:|------|---------|
| 1 | CRM erpSync 用 Dexie 打开 forge_erp_db | DB 名猜错了 |
| 2 | CRM erpSync 用原生 IndexedDB | Schema 不匹配 |
| 3 | ERP readTable 加 refreshCacheFromDb | 缓存优先于 Dexie 水合 |
| 4 | ERP baseDataApi 直读 Dexie | 函数改为 async 后调用方不兼容 |
| 5 | CRM 用与 ERP 同款 Dexie schema | DB 名仍然猜错 |
| 6 | localStorage 桥 | 重部署会丢数据 |

## Codex 一次性修好的原因

Codex 同时读取了两边的完整源码,发现了根因:
- **ERP Dexie DB 名是 `qs_inventory_db`,不是 `forge_erp_db`**
- CRM 所有版本都在往不存在的 DB 里写

## 教训

- **不确定配置就查源码,不靠记忆或猜测**
- **DB 名/表名/字段名必须在操作前从源码确认**
- **全量诊断(同时读两边源码)比逐次打补丁高效**
