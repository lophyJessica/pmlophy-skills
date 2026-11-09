# 部署常见坑位

## `<base href>` 与 HashRouter 冲突

**症状**: 部署到子路径后,内部导航跳转到域名根路径而非项目路径。

**根因**: HTML 的 `<base href="/project/xxx/">` 会劫持所有 `<a>` 和 `<Link>` 的 href,导致 HashRouter 路由失效。

**诊断**: 用 Puppeteer 实测:
```js
const pp = require('puppeteer');
const b = await pp.launch({headless:true,args:['--no-sandbox']});
const p = await b.newPage();
p.on('framenavigated', f => console.log('NAV:', f.url()));
await p.goto('https://pmlophy.com/project/copy-wms/', {waitUntil:'networkidle2'});
// 展开菜单,点击目标按钮
await p.evaluate(() => { /* click buttons */ });
console.log('FINAL:', p.url());
```

**修复**: 删除 `<base href="...">` 标签。HashRouter 不需要它。

## 路由使用 `<button>` 而非 `<a>`

**症状**: 侧边栏导航是 `<button>` 元素,`<base>` 和 `<Link>` 都不适用。

**诊断**: `document.querySelectorAll('a')` 找不到导航元素 → 检查 `button` 标签。

**修复**: 确认按钮的 onClick handler 使用绝对路径(`/project/xxx/...`)导航,而非相对路径。

## 导航路径重复拼接（2026-07-22 copy-wms 实战）

**症状**: Puppeteer 实测点击按钮后 URL 变成 `/project/copy-wms/project/copy-wms/wave/management`(路径重复两次)。

**根因**: 菜单使用 `<button>` 标签,onClick handler 调用 `navigate()` 时传入**相对路径**(不带开头的 `/`),浏览器在 `/project/copy-wms/` 页面下将相对路径追加到当前路径末尾。

**修复**: 所有 navigate 调用必须使用**绝对路径**(以 `/project/xxx/` 开头)。Codex 可能多次修复不干净 — 批量搜索裸路径 `/putaway` `/wave` `/inbound` 确认清零。

## 导航行为不一致

**症状**: 同一菜单下有的按钮跳正确(`/project/copy-wms/wave/management`),有的跳错(`/project/copy-wms/project/copy-wms/putaway/management`)。

**根因**: 部分按钮用 `${B}/xxx`(B="/project/copy-wms"),部分直接用 `navigate('putaway/management')`(相对路径)。

**修复**: 统一所有导航为 `${B}/xxx` 格式 — 必须逐个按钮验证,不可只改一两个。

## 子路径部署检查清单

每次新项目部署到 `/project/xxx/` 时检查:
- [ ] vite.config.ts 的 `base` = `/project/xxx/`
- [ ] index.html 中**无** `<base href>` 标签
- [ ] HashRouter 的 `basename`(如有)已配置
- [ ] 所有导航路径为绝对路径(以 `/project/xxx/` 开头)
- [ ] nginx location 块已添加 `try_files $uri $uri/ /project/xxx/index.html`
