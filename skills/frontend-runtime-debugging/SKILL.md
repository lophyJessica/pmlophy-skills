---
name: frontend-runtime-debugging
description: "前端运行时 bug 分层取证调试——源码/构建/部署/React fiber/DOM 五层断言排查法,Playwright 无缓存复现,props有但DOM无/样式丢失/元素属性被劫持等反直觉 bug 的定位套路。当用户报'页面不生效/样式没变化/部署了没效果'且常规检查都正常时使用。"
version: 1.0.0
category: software-development
---

# Frontend Runtime Debugging

## Overview

"代码明明改了、部署了、bundle 也是新的，但页面就是不对" —— 这类 bug 的共同点：**每一层看起来都对，问题藏在运行时**。常规 grep 目测不够，必须分层取证、每层用可机器验证的断言。

## 五层取证法（自上而下，每层必须实锤后才进下一层）

1. **源码层**：grep 确认改动存在（`rg` 精确到文件:行号）
2. **构建层**：dist bundle 里 grep 改动特征（注意 minify 后变量名被压缩、共享常量会被提升到 chunk 前部——**字面量不在使用点附近 ≠ 缺失**，应 grep 使用点引用的压缩变量名并回查其定义）
3. **部署层**：远端直接 curl/ls 实锤文件内容，不信传输日志；同时确认浏览器实际加载的 bundle 文件名（`document.querySelectorAll('script[src]')`）
4. **React 层**：Playwright 里读 fiber —— `Object.keys(el).find(k => k.startsWith('__reactFiber$'))` → `fiber.memoizedProps.style`。props 有 = React 认为已写入
5. **DOM 层**：`el.getAttribute('style')` + `getComputedStyle(el)` + **`el.style instanceof CSSStyleDeclaration`**

## 关键判别式：props 有但 DOM 没有

说明写入目标被劫持。最高频元凶：**HTML form named control 遮蔽** —— `<Form.Item name="style">` 会让 named property 遮蔽 `HTMLFormElement.style` 原生 accessor，React 的样式写入全部静默失败进假对象。

决定性验证：`el.style instanceof CSSStyleDeclaration` —— false 即坐实；`el.style.setProperty is not a function` 是同一结论的抛错形态。

详见 [references/dom-named-control-shadowing-case.md](references/dom-named-control-shadowing-case.md) —— 完整案例含有效排查顺序、钩子陷阱、修复模式。

## Playwright 复现纪律

- 必须全新 browser context（无缓存/无登录态残留），`page.addInitScript` 做拦截钩子
- 钩子可能落空：React bundle 若早于钩子缓存了原型引用，**钩子全空 ≠ 没有写入**；此时改用属性身份断言（instanceof / 方法存在性）比监听更可靠
- 对比实验设计：同一 context 内访问正常页 vs 异常页，逐字段对比（styleAttr / fiberProps / formCount / inDoc）
- 手动 setAttribute 后触发 re-render 再读 —— 区分"没写入"和"写入后被清"

## Pitfalls

- ❌ **拿源码静态 grep 的字符串判定「渲染结果没有」** —— HTML/JS 常在渲染时补齐格式（如 `value.length === 16 ? value + ':00' : value` 给时间补秒、`padStart` 补零、模板拼接单位），源码里根本没有最终呈现的那个字符串。搜「14:20:00」零命中不代表页面显示到分。判定「用户看到的形态」只有三条路：读渲染/格式化函数本体、在真实页面取文本（DOM/截图）、或按数据源格式反推。**更不许据此指控用户「没 push/改动丢了」——先证明渲染路径再说，错了就立刻收回并说明是检索方法的问题。**
- ❌ 只信 AI 的自检报告文字 —— 要求提供可复核证据（bundle grep 输出、fiber 读值），报告与实测矛盾时以实测为准
- ❌ 目测截图判断"间距没变" —— 16px→24px 肉眼无感，改样式要么卡片化/背景色这类强视觉差异，要么直接读 computed style
- ❌ 怀疑缓存前先确认"哪些页面正常哪些异常"——同构页面 A 正常 B 异常 = 排除全局缓存，聚焦 B 页独有代码路径
- ❌ minified bundle 里 grep 不到原始字面量就下结论"改动没进产物" —— 先找使用点的压缩变量，回查定义位置
- ❌ 拿截图/视觉识别去判定控件是否可填 —— 截图里 disabled 输入框与可填输入框同形：占位符「请输入X」、红色必填报错框都会照常呈现，禁止态提示（鼠标悬停显示禁止符号）根本不进画面。可填性只能取自源码（disabled/readonly 属性）或人工在实机上悬停确认，视觉结论与源码结论不一致时不要当成"两种态"或"版本不一致"上报
- ❌ 给 AI agent 出「重做交互原型」的指令只给中文描述不给结构化事实源 —— 指令越细，模型自由发挥的空间越大：17 个字段/枚举/空值写一大段散文，它每渲染一个就可能丢一个。改成先落一份结构化字段表（TSV：字段名/归属位置/枚举/空值写法）push 进仓库，指令里只说「字段只从这份文件取」——渲染由数据驱动，字段名和枚举想错都没空间；同一口径返工超过一轮时必须切到这个模式
