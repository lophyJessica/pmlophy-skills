# 案例：React inline style "消失" — HTML form named control 遮蔽原生属性

（forge-scrm 2026-08-31，脚本列表页筛选卡片）

## 现象
antd `<Form style={cardStyle}>` 卡片样式只在 8 个同构列表页中的 1 个不渲染，其余正常。换浏览器/无痕/清缓存/重新部署均复现。无 JS 报错。

## 证据链（按排查顺序）
1. 源码层：`ScriptList.tsx` 确认 `style={FILTER_CARD_STYLE}` 引用存在 ✅
2. 构建层：线上 bundle 里脚本模块 `style:t`，`t={...Ji}`，`Ji={background:"#fafafa",...}` 完整 ✅（教训：minify 后共享常量提升到 chunk 前部，grep 字面量不在使用点附近 ≠ 缺失，要 grep 压缩变量名并回查定义）
3. 部署层：远端 curl 首页拿到新 bundle 文件名一致 ✅
4. React 层（Playwright 全新 context + 登录）：form DOM 的 `__reactFiber$` → `memoizedProps.style` 有完整样式对象 ✅
5. DOM 层：`getAttribute('style')` = null ❌ —— props 有但 DOM 无

## 收敛过程
- 排除缓存：换浏览器+无痕+Playwright 全新 context 均复现；服务端直验 bundle 是新的
- 排除路由懒加载/重复组件：bundle 里 `title:"脚本列表"` 第二处是详情页占位文案；App.tsx 静态 import
- 排除"写入后被删"：hook `removeAttribute`、`CSSStyleDeclaration.prototype.setProperty/cssText`、`setAttribute` 全空；手动 setAttribute 后触发 re-render 不被清
- **决定性一击**：对该 form 调 `el.style.setProperty(...)` 抛 `TypeError: el.style.setProperty is not a function`；`el.style instanceof CSSStyleDeclaration === false` —— style 属性被替换成了普通对象

## 根因
`<Form.Item name="style">`（语言风格下拉）——HTML 规范中 form 的 named control 遮蔽 `HTMLFormElement.style` 原生 accessor（named property 优先于原型链）。React 逐条写 `node.style.background=...` 全部写进假对象，静默失败。其他 7 页无 `name="style"` 控件故正常。

## 修复
字段改名 `style` → `script_style`，`load()` 里解构后映射回请求参数 `style`（后端契约零改动）。禁止 useEffect 手写 DOM 样式糊补丁。部署后 Playwright 终验三项断言全过：instanceof=true / attr 含 background / computedBg=rgb(250,250,250)。

## 中途修正记录（防重蹈）
- 第一轮错误结论"bundle 缺样式引用"：因用"使用点附近 800 字符内有无 fafafa 字面量"判断——minify 常量提升导致假阴性。正确做法：grep 压缩变量引用 `style:Ji` 再回查 `Ji=` 定义。
- 第二轮修复（独立对象 `{...FILTER_CARD_STYLE}` + `key="scripts-filter"`）无效——根因不是 React diff，别在错误层修。
- AI 自检报告称"沙箱权限不足无法本地 Playwright 回归"——属实时情，最终以线上真实环境验证收口。