---
name: gemini-frontend-rebuild
description: 用 Gemini/Antigravity 复刻或升级前端页面——沉淀公共组件、还原老系统风格、批量改样式。当用户说"优化页面样式/复刻页面/改UI/批量调整前端"时使用。
trigger:
  - User says "优化页面样式" / "复刻页面" / "改UI" / "批量调整前端"
  - Task involves full-page rebuild or style overhaul in forge-erp/wms
---

# Gemini 前端复刻/样式升级指令模板

融合了"资深前端还原工程师"模板的执行流程和五段式指令的防跑偏机制。

## 适用场景
- 从 0 复刻一个老系统页面
- 批量优化已有项目的 UI 样式(配色/字体/间距/组件)
- 参考一个系统风格,应用到另一个系统

## 模板

```plaintext
Context:
你是一名资深前端还原工程师。当前项目是 forge-erp 或 forge-wms（React + Vite + Tailwind CSS + HashRouter）。
项目已有完整的侧边栏、表格、表单等公共组件。本次任务只需要改样式和交互，不新增功能模块。

参考页面：本项目的现有页面风格（默认不另找参考，遵循当前项目的配色/字体/间距/组件规范）
目标页面：[具体页面名称或"全站所有页面"]
目标浏览器尺寸：1920×1080

Request:
1. 先扫描项目现有组件结构（Sidebar/TopNav/DataTable/FilterForm/Modal 等），优先复用不改风格
2. 分析参考页面的：配色方案、字体层级、间距密度、表格风格、卡片阴影、状态标签配色
3. 将以上风格特征应用到目标页面，保持布局和业务逻辑不变
4. 状态标签统一中文化（DRAFT→草稿、CONFIRMED→已确认 等）
5. 完成后 npm run build 验证编译

Output format:
- 改动了哪些文件 + 各自改了哪些样式
- 编译成功 → dist.zip
- 编译失败 → 逐条错误明细

红线禁止:
- 只改样式和交互，不新增/删除任何业务功能
- 只改样式，不碰路由、API、数据逻辑
- 禁止改 vite.config、tsconfig、package.json
- 禁止 npm audit fix / npm update
- 禁止 git commit 或 push
- 不确定的颜色/间距/字体，使用低风险假设并在结果中说明

Checkpoint:
- 编译通过 → 打包 dist.zip
- 编译失败 → 只报错误，等我处理
```

## 关键参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| 参考页面 | Gemini 需要看的"目标风格" | 一个 URL 或详细描述 |
| 目标页面 | 要改哪些页面 | "全站所有页面" 或 "入库管理模块" |
| 公共组件 | 项目的复用组件名 | Sidebar/TopNav/DataTable 等 |

## 实战经验

1. 参考页面用本项目现有风格即可,不需要每次找外部 URL
2. 改全站样式时,优先沉淀公共组件(状态标签/表格/筛选栏),后续改单页只需调参数
3. 状态中文化是性价比最高的改动——英文标签改成中文后,整个系统看起来会像"正式产品"而非 demo
4. 完成后必须人工审计:状态标签是否齐全、配色是否一致、表格密度是否合适

## 部署到 VPS 的注意事项

> 详见 `references/forge-deploy-pitfalls.md` —— 完整部署坑与恢复 SOP。

### 文件权限
`write_file` 写入 `/var/www/pmlophy.com/` 下的文件默认权限可能是 600(仅 root 可读),nginx 运行在 www-data 用户下无法读取 → 403。
部署后必须 `chmod 644` 修正,或用 terminal + cat 直接写避免权限问题。

### nginx 配置顺序
具体子路径的 location 块(`/project/xxx/docs/flow/`)必须放在通用 location 块(`/project/xxx/`)**之前**,否则通用块的 try_files 会先匹配。
本次踩过的坑:docs/flow/ 和 docs/api/ 的 location 块放错了顺序,403 排查了 3 轮才发现。

### markdown 文件直接访问会触发下载
nginx 默认把 .md 文件当 application/octet-stream 返回 → 浏览器直接下载。
解法:创建 HTML 包装页,用 marked.js + mermaid.js 渲染 .md 内容,nginx 默认 serve index.html。
```html
<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head><body><div id="content"></div><script>
mermaid.initialize({startOnLoad:false,theme:'dark'});
fetch('产品结构图_交互流程.md').then(r=>r.text()).then(md=>{
  document.getElementById('content').innerHTML=marked.parse(md);
  mermaid.run({querySelector:'.language-mermaid'});
});
</script></body></html>
```

## 部署后 docs 路径规范

forge-erp 和 forge-wms 的 docs/ 目录遵循统一结构:

| 路径 | 内容 |
|------|------|
| `/docs/api/` | Swagger API 文档(index.html + api-spec.yaml + er.html) |
| `/docs/flow/` | 产品结构图_交互流程.md(mermaid 流程图) |

门户首页: `pmlophy.com/index.html`,两个卡片链接到 ERP 和 WMS,底部署名刘龙飞作品集。
调整首页卡片信息用 patch 工具直接改 index.html,不要重写整个文件。

## 关键坑

### Hermes 命令官铁律:只给指令,不动手改
**Hermes 不识别图片、不擅长 UI 微调。** 前端/视觉类任务,只给反重力或 Gemini 写指令,**不自作主张直接改文件**。用户与 Gemini 可以直接截图→看→改,效率高十倍。Hermes 手动改 → 用户再审 → 浪费时间和 token。用户不说"你改",绝不碰文件。

### 并行编译覆盖
多个 Agent(Codex/反重力)并行改代码时,**每个 Agent 只改源码不执行 `npm run build`**。全部改完后手动一次性 build。原因:并行 build 产物互相覆盖,后部署的会清掉先部署的改动。实测:盘点+报损+库存查询三个 Agent 并行 build → 只有最后一个生效。

指令模板中已默认使用 `不要 npm run build`,确保并行安全。用户手动 build 后一次性发 dist。

### 五段式完整性
A2A 指令必须包含完整的五段:**Context → Request → Output format → 红线禁止 → Checkpoint**。少任何一段都会降低 Agent 输出质量:
- 缺 Output format → Agent 输出格式不可预测,难以验证
- 缺 Checkpoint → Agent 不清楚何时停止、如何验收
- 缺 红线禁止 → Agent 可能改不该改的文件

### dist 部署会冲掉非 dist 文件
`rm -rf 目标目录/* && cp -r dist/* 目标目录/` 会清空目标目录中所有文件,包括手动添加的非构建产物(如 docs/flow/index.html、flowchart.md 等)。部署后必须检查并恢复这些文件。本次踩坑:部署后 docs/flow/ 和 docs/api/ 被清空,导致产品结构图页面 403。

### VPS 无法 push GitHub（铁律）
VPS 没有 GitHub token,任何 git commit + push 都会失败。**绝对不要从 VPS 做 git push**,也不要在 VPS 上 commit 后告诉用户 pull——用户 pull 不到因为根本没 push 上去。正确做法:需要修改的文件直接发内容给用户,或通过飞书附件发,让用户在自己的 Mac 上创建/修改,然后自己 commit + push。

### 五段式 vs 微调式：两种 AI 工作模式
用户在 2026-07-15 的实战中验证了:**结构化逻辑修改**(如"加审核按钮")用五段式,一步到位;**UI 样式微调**(如"颜色调冷""间距加大")无法一步到位,需要多轮迭代。因为 UI 微调的验收标准是"看着舒服",无法像"编译通过"那样精确描述。Agent 只能猜用户偏好,猜偏了再修,修完再猜——这不是失败,是 UI 调优的正常节奏。

### mermaid 图缩放：必须用"局部视口滚动"
给 mermaid SVG 加缩放时,容器大小必须固定,缩放后内容在容器内滚动(overflow:auto),**不能同步放大容器导致页面被撑开**。用户 23:07 纠正的黄金原则:"只要被放大,就永远不会触发到纵向滚动条——因为你做了放大时所在控件窗口同步放大,我不需要这样,请关闭这样的放大方式,放大后窗口大小不变。"正确模式:固定容器 + SVG transform:scale() + overflow:auto。

### 谋定而后动（铁律，适用所有场景）
动手前先想:前提条件齐了没?东西在哪?做完这步到哪?不确定就问一句,绝不手比脑子快。

### 用例数据推演是前端的前置闸门（铁律，不可跳过）
PRD 文档里写了用例数据推演,必须先推演至少一遍后再写前端 Demo。**直接跳过推演=白写了用例文档。** 推演不过关不能进入前端原型阶段。2026-07-17违规:CRM三个模块用例齐全,但直接跳搭前端,被当场纠正。

### 发文件/指令前先 git pull 确认远程状态（铁律）
用户已 push 到 GitHub 的文件,Hermes 不重复创建、不重复发送 MEDIA。发之前先 git pull 确认——避免出现"我刚发过了,你又发一遍"的无效循环。2026-07-17违规:三个 context 文件已 push,被重新 write_file + MEDIA 发送。

### 单线程对话,不并列追问（铁律）
一个任务完成 → 用户确认 → 再下一个。不等状态、不等进度、不等猜测。不并行追问"那个好了没""编译完了吗"。除非用户要求并行,否则严格单线。并行任务用 delegate_task 拆子 Agent。

### A2A 指令及其他长文本：发 md 文件，不发对话框文本
用户要求 PRD、context、A2A 指令、模板等长文本以 `.md` 文件通过 MEDIA 发送,**不在对话框内粘贴大段文本**。除非用户明确说"文本发我"。用户需留存归类到项目提示词文件夹。

## 和五段式的关系

五段式更适合**修改已有页面的指定逻辑**(如"盘点加审核按钮"),这个模板更适合**翻新整个页面的视觉样式**。两者可以组合:先翻新样式,再用五段式精准修逻辑。

## 四种 UI 复刻方案（按数据源分级）

| 方案 | 数据源 | 适合场景 | 工具 |
|------|--------|---------|------|
| **A 源码** | 研发给代码 | 自己公司老系统改造 | 反重力/Codex |
| **B 设计稿** | UI 给 Figma+组件库 | 新项目从设计稿还原 | Figma MCP |
| **C 截屏** | 截图→Agent看→改 | 竞品/无登录/UI微调 | Gemini(本skill) |
| **D 浏览器自动化** | @chrome直接抓DOM | 公开页/有Demo账号 | Codex @chrome |

四种方案可交叉使用:
- A+D:老系统改造——@chrome看现状,源码精准改
- B+C:UED走查——设计稿截图vs开发截图,Agent对齐
- C+D:竞品分析——@chrome抓公开页,C补充内页截图

参见 `references/codex-chrome-browser-clone.md` —— @chrome 复刻 WMS 实操记录。
