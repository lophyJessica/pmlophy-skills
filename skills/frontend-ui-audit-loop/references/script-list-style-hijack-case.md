# 实战案例：脚本列表筛选卡片 style 丢失（2026-08-31）

## 现象
forge-scrm 部署"列表页筛选区卡片化"（8 页统一 FILTER_CARD_STYLE）后，7 页正常，唯独 /scripts 筛选 form 无任何 style（getAttribute('style') === null，computed background transparent / border 0 / padding 0）。

## 排查时间线（含弯路）
1. 用户实测截图反馈"间距太小" → 第一轮修复 marginBottom 16→24 → 用户仍说没变（16→24 视觉差 8px 无感，这是规范与观感落差，不是执行问题）
2. 用户拍板方案 A：筛选区卡片化（#fafafa 底+边框+圆角+padding 16）
3. 部署后用户实测：其他 7 页有效果，脚本列表还是老样子
4. 杰西卡 grep bundle "正文关键词"附近 800 字符找 fafafa 字面量 → 未找到 → **误判"构建产物缺样式引用"** → 出指令让 Codex 清缓存重建 → 重建后产物 hash 不变
5. Codex 纠正：`style:Ji` 引用存在于脚本模块，`Ji={...}` 定义被 Rollup 提升到 chunk 前部——**字面量不在使用点附近是正常形态，此前的检查方法无效**
6. 杰西卡出 ego 浏览器实测指令 → 实测 7 页有卡片、脚本页 form 的 style 属性整体缺失（computed 全空、styleAttr null）
7. Codex 推断"跨路由 fiber 复用导致共享 style 对象未重写 DOM"，修复 = 每渲染新建 `{...FILTER_CARD_STYLE}` + 稳定 `key="scripts-filter"` 强制重挂
8. 部署后用户换浏览器实测仍无效 → 杰西卡 VPS 上 Playwright 深挖

## Playwright 证据链（VPS /tmp/pwtest/*.cjs）
- check2: 同一 session 对比 /materials（styleAttr 完整）vs /scripts（styleAttr null）→ **稳定复现，排除缓存/浏览器**
- check5: 读 React fiber —— `__reactProps$` 上 `style` **有完整对象**；DOM attribute 却是 null
- check16/28: 脚本页与资料页 host fiber 的 memoizedProps.style / flags（2097156）完全一致
- check17/31/32: hook `removeAttribute`、`CSSStyleDeclaration.prototype.cssText/setProperty/逐条属性赋值` **全部零命中**——React 的写入没有走这些路径
- check18/19/20/21: 手动 setAttribute 写入 style → 不被清除；React 重渲染（输入触发/查询按钮）后仍保留 → **没有任何东西在删 style**
- **check37（决定性）**: `el.style.setProperty is not a function` → 该 form 元素的 `style` 属性被替换成了普通 JS 对象，不是 CSSStyleDeclaration！

## 根因结论
脚本页某处代码把 form 元素的 `style` 属性劫持/替换成了普通对象。React commit 时逐条赋值（`node.style.background = ...`）写进了假对象（普通对象赋值不报错），DOM attribute 永远不更新。fiber props 层样式完好、DOM 层永远丢失——这就是"props 有、DOM 无"的完整解释。

## 修复方向（32-b 指令，未执行）
1. 全仓搜 `defineProperty`、`.style =` 赋值、原型篡改
2. 重点怀疑脚本页独有代码路径：`useSearchParams` + `form.setFieldValue` useEffect、antd Form 与 rc-field-form 实例交互
3. 运行时定位：挂载后立即 `form.style instanceof CSSStyleDeclaration` 检查 + 二分注释法找替换发生的代码
4. 修复后本地 build + Playwright 验证 `/scripts` getAttribute('style') 含 background，`/materials` 回归

## 可复用的调试脚本模式
```js
// Playwright 读 React fiber props（放 /tmp/pwtest/，npm i playwright@1.49.1 + install chromium）
const fk = Object.keys(el).find(k => k.startsWith('__reactFiber$'));
const pk = Object.keys(el).find(k => k.startsWith('__reactProps$'));
const propsStyle = el[pk]?.style;           // React 层
const domStyle = el.getAttribute('style');  // DOM 层
const isRealCSS = el.style instanceof CSSStyleDeclaration; // API 身份
```

## 元教训
- 弯路 1：字面量邻近性检查 minified bundle（Rollup 提升共享常量，无效）
- 弯路 2：归因缓存（需 Playwright 全新 context 复现才能排除/确认）
- 弯路 3：Codex 第一轮修复（新建对象+key）基于 fiber 复用猜想，未先实证 API 身份——**应在 fiber props/DOM 对比出矛盾后第一时间查元素 API 完整性**
- 正确顺序：源码 → bundle 变量引用+定义 → 服务端 hash → DOM attribute → fiber props → **元素 API 身份** → 劫持源定位
