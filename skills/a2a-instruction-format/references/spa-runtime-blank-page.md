# SPA 运行时空白页调试（浏览器注入错误监听器）

> 2026-08-13 forge-erp 实测：点击"销售订单"→ 页面空白，nginx/路由/Dexie 全正常。
> 根因：初始订单数据引用旧商品编码 SKU001，商品表已迁到 SP-xxx → getSalesOrders 校验商品抛错 → React 渲染崩 → 白屏。

## 症状特征

- 页面能登录、主工作台正常，但点击某菜单/路由 → 全白（root 空、React 未挂载）
- 直接导航到该 URL 也白（稳定复现）
- nginx 200、bundle 加载成功、Dexie 表存在数据正常——排除部署/数据层问题
- 即：**React 组件渲染期抛错，无 ErrorBoundary → 整树卸载 → 白屏**

## 诊断路径（顺序执行）

### 1. 确认是渲染崩而非路由/部署

```js
// browser_console 执行
(function(){ return {
  rootChildren: document.getElementById('root') ? document.getElementById('root').childElementCount : -1,
  reactRoot: !!(window.__REACT_DEVTOOLS_GLOBAL_HOOK__ && window.__REACT_DEVTOOLS_GLOBAL_HOOK__.renderers),
  url: location.href
}; })()
```
- `rootChildren: 0` + `reactRoot: false` = React 加载后卸载（渲染崩）
- bundle 加载成功：`performance.getEntriesByType('resource')` 里能看到 `index-*.js`

### 2. 排除 Dexie/数据层（快速）

直接浏览器里打开 IndexedDB 查表：
```js
(async function(){ const req = indexedDB.open('DB名'); const db = await new Promise((res,rej)=>{req.onsuccess=()=>res(req.result);req.onerror=()=>rej(req.error)});
const tables = Array.from(db.objectStoreNames); /* 查具体表数据/枚举值分布 */ })()
```
DB 名从源码 `new Dexie('...')` 确认（不猜）。表存在+数据正常 → 不是数据层。

### 3. 核心技巧：注入错误监听器捕获 React 渲染错误

React 渲染错误默认只给空 message 的 exception（browser_console 的 js_errors 是 `{"message":""}`——没用）。
**关键：先在正常页注入监听器，再用 SPA 内部导航触发崩溃页**（内部导航不刷新页面——监听器保留）：

```js
// ① 在正常页（如首页）browser_console 执行——注入监听器
(function(){ window.__errs = [];
  const origErr = console.error;
  console.error = function(){ window.__errs.push({type:'console.error', args: Array.from(arguments).map(a=>{ try{ return typeof a==='string'?a:(a&&a.message?a.message:JSON.stringify(a).substring(0,300)); }catch(e){return String(a);} }).join(' | ')}); origErr.apply(console, arguments); };
  window.addEventListener('error', e => { window.__errs.push({type:'window.error', msg:e.message, stack:e.error?String(e.error.stack).substring(0,600):''}); });
  window.addEventListener('unhandledrejection', e => { window.__errs.push({type:'rejection', reason:String(e.reason).substring(0,300)}); });
  return 'listeners installed';
})()
```

```js
// ② 点菜单（browser_click 触发 SPA 内部导航）→ 页面变白
// ③ browser_console 读捕获的错误
JSON.stringify(window.__errs || 'NO LISTENER', null, 2)
```

捕获到类似：
```
Uncaught Error: 商品 SKU001 不存在
  at Ak (index.js:486:401342)
  at D5e ...
  at Pk (读取订单)
  at Object.getSalesOrders ...
```
= 渲染期数据校验抛错。**错误消息直接给出根因**（哪个实体找不到），堆栈给出调用链（哪个 API 在读数据时校验）。

⚠️ 不要直接 `browser_navigate` 到崩溃 URL 再读 console——刷新会清掉监听器，且 React 错误可能不落 window.onerror。**必须走"正常页注入 → 内部导航触发 → 读 __errs"三步**。

## 根因模式：数据/代码不一致（本案例）

商品编码体系迁移（SKU-xxx → SP-xxx）后，代码里的**初始数据**（initialOrders()）仍引用旧编码：
- `initialOrders()` 的订单 items 引用 SKU001/SKU002
- `getSalesOrders()` 读订单 → 构造订单项时 `getSalesProducts().find(p => p.code === productCode)` 校验 → 找不到 → `throw new Error('商品 SKU001 不存在')`
- 组件渲染期调用 getSalesOrders → 抛错 → React 崩 → 白屏

**修复**：把初始数据的旧编码换成商品表实际存在的编码（SP-001~SP-007）——数据与代码对齐。
**预防**：改编码体系（SKU→SP、前缀变更）时，同步排查所有 mock 初始数据（订单/出库单/退货单 items 的商品引用）——grep 旧前缀。

## 通用排查清单（SPA 白屏）

| 层 | 检查 | 快速验证 |
|---|---|---|
| 部署 | nginx 200？bundle 加载？ | curl 页面 + performance entries |
| 路由 | 路由注册？basename？ | 源码 grep Route/path |
| 数据 | Dexie 表/枚举？ | 浏览器直接查 IndexedDB |
| **渲染** | **组件渲染期同步调用是否抛错** | **错误监听器注入法（上面第 3 步）** |
| 状态 | 渲染期顶层同步调用（非 useEffect） | 源码读组件头部：`const x = api.getX()` 在 return 前 = 渲染期调用，抛错即崩 |

重点怀疑：组件顶层同步数据调用（`const customers = api.getCustomers()` 这类——不在 useEffect 里），尤其带 `.filter()` 后访问属性、`find()` 后可能 undefined、枚举映射表 `META[status].label` 之类。
