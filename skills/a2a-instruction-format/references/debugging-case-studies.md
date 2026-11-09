# 实战调试案例：手工 Patch 循环 vs 全量诊断

> 来源: forge 项目 2026-07-18 至 2026-07-22

## 铁律: 3轮失败 = 停止手工,全量诊断

同一 bug 修复 >= 3 轮仍未解决 → 立即停止 → 发给 Codex 做全量诊断(同时读两边全部源码)。

## 案例1: CRM转客户→ERP客户列表看不到(6轮失败→Codex一次修复)

**手工尝试(全部失败)**:
1. 加 refreshCacheFromDb → 缓存仍优先于 Dexie
2. baseDataApi 改 async 直读 Dexie → 调用方没 await
3. 用 localStorage 桥接 → 数据不同步
4. CRM erpSync 用 Dexie 打开 ERP DB → schema 版本冲突
5. 用原生 IndexedDB → 仍读不到
6. useLiveQuery 直读 Dexie → 仍未解决

**Codex 全量诊断**:
- 读 ERP db/index.ts 完整源码 → DB 名是 `qs_inventory_db`
- 读 CRM erpSync.ts → 写的 DB 名是 `forge_erp_db`
- 发现 erpSync.ts 不在 Git 仓库(每次 build 丢失)
- 发现 LeadDetail.tsx 没 import erpSync
- **根因: DB 名不匹配 + 文件未提交 + import 缺失,三个问题**

## 案例2: copy-wms 路由(7轮失败→Puppeteer诊断)

**手工尝试(全部失败)**: vite base / nginx / HashRouter basename / a href替换 / base标签 / menu path / navigate绝对路径

**Puppeteer 诊断**: 打开页面→抓 DOM→发现导航全是 `<button>` 不是 `<a>`→点击抓到实际 URL 相对路径拼接→定位根源

## Codex 全量诊断指令模板

```plaintext
Context:
[系统A]和[系统B]之间的[功能]不工作。两系统均在 pmlophy.com 同域名下。
系统A: [技术栈/DB名/关键文件路径]
系统B: [技术栈/DB名/关键文件路径]

Request:
全量检查并修复[功能],按以下顺序:
1. 读取[系统A关键文件]完整内容
2. 读取[系统B关键文件]完整内容  
3. 逐行对比,找出不一致(DB名/schema/字段/调用传参)
4. 列出所有问题
5. 逐一修复
6. 两系统分别 npm run build,打包 dist

输出: 诊断结果 → 修复内容 → dist.zip

Checkpoint: dist→VPS部署→验证
```
