# React SPA 白屏调试（浏览器注入错误监听——0813 forge-erp 实测）

## 症状

点击菜单/路由后页面**全空白**（无报错提示、无 loading、无内容）。URL 变了但 `#root` 空。

## 核心判断：白屏 = React 渲染期抛错（不是路由/nginx 问题）

- 登录页/首页正常、某路由空白 → **该组件渲染崩**（React 无 ErrorBoundary 时整树卸载 → 白屏）
- 直接导航该路由也空白 = 稳定复现，可调试
- 先排除：nginx 404（页面 title 能出 = index.html 加载了）、路由未注册（grep App.tsx 路由注册）

## 调试流程（浏览器工具实测路径——最快）

### 1. 基础排查（排除数据/环境问题）
```js
// 检查 React 是否挂载
document.getElementById('root').childElementCount  // 0 = 没挂载
// 检查 IndexedDB 数据是否正常（Dexie 应用）
indexedDB.databases()  // DB 存在？
// 读具体表数据（如 products/customers）——确认不是"表数据坏了"
```

### 2. 注入错误监听（关键一步——React 内部错误 console 面板经常只显示空 message）
```js
window.__errs = [];
const origErr = console.error;
console.error = function(){ window.__errs.push({type:'console.error', args: Array.from(arguments).map(a => { try { return typeof a === 'string' ? a : (a && a.message ? a.message : JSON.stringify(a).substring(0,300)); } catch(e){ return String(a); } }).join(' | ')}); origErr.apply(console, arguments); };
window.addEventListener('error', e => { window.__errs.push({type:'window.error', msg: e.message, stack: e.error ? String(e.error.stack).substring(0,600) : ''}); });
window.addEventListener('unhandledrejection', e => { window.__errs.push({type:'rejection', reason: String(e.reason).substring(0,300)}); });
```

### 3. 触发崩溃（关键：用【内部导航】而非整页刷新——监听器保留在 window 上）
- 先导航到正常页（首页/登录后主工作台）→ 装监听 → **点菜单/链接触发目标路由**（SPA 内部导航，页面不刷新，监听器不丢）
- 直接 `location.reload()` 或 browser_navigate 整页刷新会**清掉监听器**——不要用
- 崩完读：`JSON.stringify(window.__errs, null, 2)`

### 4. 读真实错误堆栈 → 追源码
```
window.error: Uncaught Error: 商品 SKU001 不存在
  at Ak (bundle.js:486:401342)         ← 压缩代码
  at getSalesOrders (bundle.js:486:410967)
```
- 用错误消息字符串在源码仓库 grep（`search_files "商品.*不存在" src/`）定位 throw 点
- 看调用链：`getSalesOrders` → 读订单 → 校验商品 → throw

## 根因模式（本案例：数据/代码不一致 → 渲染期 throw）

forge-erp 销售订单页白屏根因：
- 商品编码体系从 `SKU-xxx` 迁移到 `SP-xxx`（商品表只有 SP-001~SP-007）
- 但 `api/sales.ts` 的 `initialOrders()` 初始订单数据仍引用旧编码 `SKU001`
- `getSalesOrders` 读订单时校验商品存在：`getSalesProducts().find(p => p.code === productCode)` → 找不到 → `throw new Error('商品 SKU001 不存在')`
- SalesOrderList 渲染期同步调用（组件顶层 `const customers = salesApi.getCustomers()` 或 useEffect 里 `loadData()`）→ throw → React 崩 → 白屏

**关键洞察**：空表也会崩（initialOrders 是代码里的初始数据，不依赖 DB 有记录）——排查时不要因"表是空的"就排除数据问题，**初始数据（initialOrders/initialXxx）也在代码里**。

## 修复模式

- 数据/代码不一致 → **改代码里的初始数据引用**（SKU001 → SP-001~SP-007，以实际商品表/权威数据为准）
- 给修复 agent 的指令要包含：根因链（哪条渲染路径 throw）、改动文件范围红线、build 验证、不 commit/push/部署
- 用户工作流：杰西卡定位根因 → 写完整指令给 Codex/Cursor/反重力 → 用户审核 → 部署

## 快速诊断清单（React 白屏）

| 检查项 | 方法 | 排除什么 |
|---|---|---|
| React 挂载 | `#root.childElementCount` | 应用是否加载 |
| 路由注册 | grep App.tsx 路由 | 路由缺失 |
| bundle 加载 | performance entries / script tags | 静态资源 404 |
| IndexedDB 数据 | indexedDB.databases() + 读表 | 数据损坏/缺失 |
| **真实错误** | **注入监听 + 内部导航触发** | **渲染期 throw（最常见根因）** |
