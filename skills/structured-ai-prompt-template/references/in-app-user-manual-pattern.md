# A2A 模式：给前端原型嵌入「用户操作手册」页

场景：forge-wms / forge-erp 这类 PRD-driven 前端原型（React+TS+Tailwind+react-router-dom v7+Dexie），
用户要一份**面向终端操作员**的操作手册，且要求手册**做进前端页面里**（不是独立 md 文档），
在导航加入口点击跳转。手册用 mermaid 流程图 + 每节点大白话操作说明**替代截图**（简版但清晰、不会像截图那样过期）。

## 先摸清再出指令（动手前必做的只读侦察）

1. **路由与导航写法**：读 `src/App.tsx`，确认路由库（本项目 react-router-dom v7）、是 `HashRouter` 还是 `BrowserRouter`、导航菜单在哪个组件（本项目 wms 是 `Layout` 里的 `<aside><nav>` 一堆 `<Link>`；erp App.tsx 1303 行更复杂）。指令要照现有写法接入，别让 executor 另起一套。
2. **PRD 里有没有现成流程图**：`grep -rl "mermaid\|flowchart\|sequenceDiagram" prd-docs/`。本项目 AGENTS.md 规范就要求「业务流程必须含 Mermaid flowchart + sequence」，所以 `prd-docs/<模块>/<单据>/<单据>_业务流程推演.md` 里**已画好流程图**——指令让 executor **直接复用**，不要重画（准确度 100% 对齐 PRD）。本次 wms 一扫有 40 处现成图。
3. **mermaid 渲染库装没装**：`grep -i mermaid package.json`。多半没装 → 指令里写明「安装 mermaid.js 依赖并同步 npm install」。
4. **范围核对**：哪些模块有 PRD、哪些只有前端页面没 PRD。**只给有 PRD 的模块写手册**。本次 wms 全模块有 PRD（可全覆盖）；erp 只有采购/库存/基础资料有 PRD，销售/零售/财务/合同**有页面但无 PRD → 红线写死不碰**。
5. **品牌口径**：读 AGENTS.md。forge 系：**强盛科技=演示公司名，Forge=产品品牌，二者并存不替换** → 写进红线，防 executor 乱改名。

## 关键技术坑：HashRouter + 子路径部署

项目用 **HashRouter**，且部署在子路径（如 `pmlophy.com/wms/#/manual`）。所以：
- 手册入口跳转**必须用 react-router 的 `<Link>` / 相对路由**，**禁止写死绝对路径 URL**（如 `/manual` 绝对路径），否则子路径部署下 404。这条要进红线。

## 手册页形态：A 方案（独立 /manual 页 + 导航入口）

用户在 A/B/C 里选了 A（最干净、像帮助中心）：
- A. 新建 `/manual` 路由 + 导航加「操作手册」入口点击跳转 ← 选这个
- B. 每个业务页加「? 帮助」抽屉（改动面大，本次没精力细化到控件）
- C. 纯 md 放 public/docs + 链接（不够产品化）

## 每个单据的手册结构：4 段，砍掉「常见问题」

用户明确否掉「常见问题」——**系统无人使用，没有 FAQ 沉淀，硬编会被面试官一问穿帮**（见 interview-preparation 的 portfolio 铁律）。最终 4 段：
1. **这个页面是干嘛的**：一句话用途 + 什么场景用
2. **业务流程图**：mermaid 渲染该单据 `_业务流程推演.md` 里现成的 flowchart
3. **流程每个节点怎么操作**：对着流程图每个关键节点，大白话讲这一步用户具体做什么动作 ← 核心，要详细
4. **关键字段怎么填**：挑必填和易错字段，不用列全部控件

页面顶部加模块锚点目录（点击跳到对应模块），方便长页面导航。

## 部署链路（对齐用户铁律：VPS 只 pull 不 push）

**不在 VPS 上生成手册。** 真实链路：
1. 用户在**本地 Mac** 用 ChatGPT Codex 模式跑指令 → 生成手册页 + 导航入口
2. 本地 `npm run dev` 验 `/#/manual` → OK 后本地 git 提交 + push 到 GitHub
3. **VPS git pull + build 部署**（先 `git fetch` 核 FF 再合，见 a2a-git-verify-loop）

## 指令要点（五段式 · 单个纯文本代码块）

- Context 段交代：技术栈、HashRouter、导航现有写法、PRD 流程图位置、品牌口径、范围限定。
- Request 段：新建 /manual 路由（HashRouter+Link 接入，防子路径 404）、装 mermaid.js、复用现有 Layout/Tailwind 风格、4 段结构、复用 prd-docs 现成 flowchart、顶部锚点目录。
- 红线禁止：不改现有业务页功能逻辑（只允许 App.tsx 加路由+导航、新增手册页、package.json 加依赖）；不碰 prd-docs/context/prompt；不改品牌名；**不编 PRD 里没有的模块/功能**（如 wms 的效期管理/数据报表 demo 没有就不写）；**不给没 PRD 的模块写手册**（erp 销售/财务）；不用绝对路径跳转；**全程只改不 commit，由用户本地统一 push**。
- Checkpoint：本地 npm run dev 访问 /#/manual 确认 入口可见/可跳转/每单据4段齐全+流程图渲染/现有页面不受影响，报改动清单等 review。

两个结构相近的项目 → **写两套独立指令**（一份全模块、一份限范围），比一套跑两次更精准。
