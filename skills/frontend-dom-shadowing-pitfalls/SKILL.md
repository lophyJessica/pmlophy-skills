---
name: frontend-dom-shadowing-pitfalls
description: 前端 DOM/HTML 命名遮蔽与样式丢失类 bug 的排查方法论与已知坑——React/antd 表单字段名遮蔽原生属性、样式写入静默失败、Playwright 运行时取证手法。
---

# 前端 DOM 遮蔽与样式静默丢失排查

## 已知坑：form 字段名遮蔽 HTML 原生属性（forge-scrm 实战案例）

**症状特征**：React 组件给元素传了完整 `style` props（fiber `memoizedProps.style` 有值），但 DOM 的 style attribute 永远为 null，computed style 无效，无任何 JS 报错。换浏览器/清缓存/重新构建部署都不解决。

**根因**：HTML 规范规定 form 内的 named control 会遮蔽 `HTMLFormElement` 的原生属性。`<Form.Item name="style">` 会让 `form.style` 返回该控件而非 CSSStyleDeclaration 实例——React 逐条写入样式时目标变成假对象，静默失败。同理危险的字段名：`style`、`name`、`title`、`action`、`method`、`id`。

**修复**：字段改名（如 `style` → `script_style`），提交时映射回后端原参数名，后端契约不变。

**预防铁律**：写 antd Form.Item 的 name 时，禁用任何 HTML 原生属性名。

## 排查方法论（样式"props 有 DOM 无"类问题）

按以下顺序收敛，每步都有可执行验证：

1. **排除缓存**：Playwright 全新 context + 无痕浏览器交叉验证；服务端 curl 确认线上 bundle hash。
2. **源码→bundle→部署三层实锤**：grep 源码引用；下载线上 bundle 查压缩后的引用（注意：Rollup 会把共享 token 提升到 chunk 前部，字面量不在使用点附近 ≠ 缺失，应查 `style:变量名` 引用而非字面量）。
3. **读 React fiber**：`Object.keys(el).find(k => k.startsWith('__reactFiber$'))` → `fiber.memoizedProps.style`。props 有 = React 层无问题，问题在 DOM 写入环节。
4. **验证 style 对象真实性**：`el.style instanceof CSSStyleDeclaration` + `el.style.setProperty` 是否抛错。**抛 TypeError = style 被替换成普通对象 = named control 遮蔽类根因**。
5. **MutationObserver / setAttribute hook 抓不到写入**不代表没问题——静默写入假对象不触发这些钩子。

## Playwright 服务器端取证模板

VPS 无 GUI 时可装 playwright@1.49.1（`npm i playwright@1.49.1 && npx playwright install chromium`）无头登录 + 读 fiber + 截图。模板见 `references/playwright-evidence.md`。

## 陷阱

- 不要把"字面量 grep 不到"当"引用缺失"（压缩器提升）。
- 手动 `setAttribute('style', ...)` 后不被清除 ≠ 没有破坏者——如果是遮蔽型根因，本来就没东西在删，只是一开始就没写进真 CSSStyleDeclaration。
- agent（Codex）声称"本地 Playwright 验证通过"不可信时，要求它给出具体断言结果；本机 Chromium 权限问题常导致它跳过验证，此时用服务器端 Playwright 或用户浏览器实测补位。

## 图标组件渲染为空 = agent 自检与用户实测矛盾的典型根因（本地 agent 交互轮常见）

**症状**：agent 自检报告打勾（DOM 里节点存在、`name` 传了值），用户浏览器实测该位置空白。

**排查顺序**：
1. 项目的组件自动注册机制是否覆盖该组件库——unplugin-vue-components 只列出显式注册进 components.d.ts 的库（如只有 VantResolver 时，`nx-*` 这类私有库组件不会自动注册），babel-import 插件只转换 import 语句、不注册全局组件。
2. 组件标签所在文件有没有显式 import——没有 import 且不在 d.ts = Vue 当未知标签渲染，产出空节点。
3. 图标名是否在项目任何地方验证过存在——只在无其他用例的组件里首次出现的图标 name，缺字形渲染就是空。DOM 有节点 ≠ 视觉可见。

**修复方向**：小图标优先纯 CSS 画法（border + rotate 画 chevron 等），零依赖、不被注册机制和图标字体连累；需要组件图标时在组件内显式 import 并选项目内已有用例的 name。

**流程教训**：本地 agent 改码但未 push 时，会话另一侧只能靠用户转发截图判断；要求 agent「改动完必须交渲染截图」并与上一版截图做文件级时间戳区分，避免反复拿旧图当新交付核对。
