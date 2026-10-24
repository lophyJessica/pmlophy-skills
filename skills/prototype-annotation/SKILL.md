---
name: prototype-annotation
description: 当要给已建好的原型或前端页面加、初始化、更新、导出页面级业务标注时用。读业务 PRD，把需求映射到界面元素，注入轻量标注运行时，标注内容单独存 Markdown，不污染原 PRD 和业务代码。适用于 HTML、React、Vue、SPA、后台系统、类 Axure、Figma 导出或静态原型页面。
---

# Vitamin Prototype Annotation

## 1. 何时用本 Skill、两种工作流入口

### 1.1 适用场景与交付物

- **适用**：已有 HTML / React / Vue / SPA / 静态原型，需要把 PRD 业务规则映射到页面区域，生成「角标 + 侧栏面板」评审体验；检查原型与 PRD 不一致；为评审与研发交接提供结构化说明。
- **交付物**：本迭代 PRD 套件下的 annotations 源文件 + 编译进原型的 `annotation.bundle.json` + 通过 §7 门禁后的可访问原型。**编译通过不等于页面上能看到角标**；以浏览器实测为准。
- **价值边界**：标注是外挂解释层（见 §2.1），不是业务 UI，不改变业务功能。

### 1.2 初始化 vs 增量更新

- **Initialization**：目标项目尚无 annotation 层（无 `annotation-kit`、无 annotations 源、或未编译 bundle）。
- **Incremental update**：已有 annotation 层，且 PRD、页面代码、锚点或标注内容有变更。
- **必须先问**：用户未明确要「初始化」还是「增量更新」时，**停下来询问**，再改文件。

## 2. 核心原则（三条模型 + 一条边界）

### 2.1 标注是外挂解释层，不污染 PRD / 业务代码

Treat annotations as an external explanation layer, not as business UI. Keep the original prototype and business PRD clean. Add only the smallest required runtime hook, selector hints, and annotation documents. The page annotation runtime is strictly read-only: never add in-page editing, drafts, save APIs, or browser-to-Markdown write-back. Content changes only by editing Markdown/config in the workspace or asking the agent to update them.

### 2.2 页面层 vs 状态层（真实路由 + DOM 状态）

标注分两层：**页面**（真实路由）与**状态**（同一 URL 下靠 DOM 区分的可见形态，如弹窗、抽屉、向导步骤、展开行）。不要把状态写成不存在的子路由。

#### 2.2.1 `page` 与 `routeMatcher`

- `page` 必须是路由表中的**代表性真实路由**（如 `App.tsx`），禁止伪造 `/engage/behaviors/modal`、`/xxx/step2` 等 SPA 不存在的路径。
- `routeMatcher` 覆盖**同一页面**的等价路由（例：表单 `engage/(create|engage-create|edit/|look/)`，列表 `engage/behaviors$`）。
- 菜单/模块路由迁移后（如 `/auth/tags` → `/engage/tags`）必须同步 `page` / `routeMatcher`，否则标注可能**静默消失**（编译仍可能通过）。

#### 2.2.2 锚点、`scopeLabel`、「需操作后查看」

- 弹窗、抽屉、展开行、向导步骤、页签内区域：**不**用独立 `page` 路径；用 `target.selector` 锚定 DOM，元素在 DOM 中才挂角标。
- 配置 `scopeLabel` 标明状态（如 `弹窗：新建/编辑行为`），面板以绿色标签展示。
- 需先操作才可见的区域：进页无角标**正常**；面板可标「需操作后查看」，**不得**判为漏标。

### 2.3 角标、`screenState` 与编号

角标数字 = `annotation.id`（runtime 直接渲染）。**宿主页、弹窗、抽屉等叠加态**须用独立 `screenState` 区分；runtime 只渲染**当前可见屏幕状态**那一套角标，避免同屏两套 `1` 撞号。`page` / `routeMatcher` 仍只描述真实路由（§2.2），不要用伪造子路由或两套配置各挂一套角标。

**角标编号与屏幕状态规则见 `STANDARD.md` §5，此处不重复。**

### 2.4 迭代生命周期（随迭代生、随上线死）

- 标注不是 CMS 全量资产：**一个迭代 = 一套 PRD 套件 = 一份 annotations**。不要把历史迭代标注继续挂在原型上，不要做全量标注。
- 本迭代源文件放在该迭代 PRD 目录（例：`03-产品设计/私域2.0一期/04-评审PRD/annotations/`）。
- `annotation.workspace.json` 的 `inputs` **仅允许**本迭代 `annotation.config.json`；**禁止**把原型 `public/annotation-kit` 编译产物列为 input（自复制、角标翻倍）。
- `output` 覆盖写入原型 `public/annotation-kit/annotation.bundle.json`。
- 默认不建 `changelog.md` / `versions/`；业务 PRD 保留变更历史。用户明确要求审计快照时，仅在 annotations 目录内维护，且不进入默认 runtime 输入。

## 3. 准备与目录（本迭代放哪、输入输出什么）

### 3.1 Required Inputs

动手前在目标项目发现：

- 原型实现：静态 HTML、React/Vite/Next、Vue/Nuxt、SPA 或构建产物。
- 业务 PRD：`prd.md`、`PRD.md`、`requirements.md`、`docs/**/*.md` 或用户指定文件。
- 已有标注：`annotations/**/*.md`、`annotation.config.json`、`annotation.workspace.json`、`annotation-kit` 或已注入 runtime。
- 可运行命令：`package.json`、`index.html` 或文档中的脚本。
- 部署目标：仅本地、静态云预览、协作评审或 Git 审阅更新。

Never assume a demo layout exists in the target project.

### 3.2 迭代内 annotations 目录与 `annotation.workspace.json`

目录选择顺序（无用户指定时）：

1. 用户指定目录。
2. 项目已有 annotations 目录则沿用。
3. 主 PRD 旁建 `annotations/`（例：`docs/prd.md` → `docs/annotations/`）。
4. **附注（多 PRD 历史模式）**：各模块标注可仍在各自 PRD 旁；用最近公共父级的 `annotation.workspace.json` 聚合编译，**不要**为共享 runtime 把所有 md 挪到单目录。当前迭代交付仍以 §2.4 单 input 为准；多 config 合并细节见 `references/annotation-authoring.md`。
5. 无 PRD 可发现时，在项目根建 `annotations/` 并在回复中说明 fallback。

勿硬编码全局路径（如固定 `docs/annotations/`）除非经上述规则选中。

### 3.3 源码与产物分离

- **源**：Markdown 块（`<!-- anno:start id=... -->` … `<!-- anno:end -->`）、`annotation.config.json`、可选 `coverage.md`。
- **产物**：`annotation.bundle.json`（可公开部署）；源 PRD 与源 Markdown 不必对外提供。
- **编译**：`scripts/compile_annotations.py` 校验映射并内联 Markdown。真实项目必须编译后再验收；仅 tiny demo 可用内联 `markdown`。
- 部署与协作环境细节见 `references/collaboration-deployment.md`（流水线门禁以 §7.1 为准）。

## 4. 端到端工作流

### 4.1 Workflow A：初始化

1. **Inspect project type and entry**
   - React/Vite/SPA：`package.json`、`src`、根 `index.html`。
   - Static HTML：相关 `.html`。
   - Built output only：runtime 注入或 bookmarklet。
   - **出口**：写明项目类型与 HTML/入口路径。**证据**：列出的路径存在。

2. **Read PRDs**
   - 保留字段、状态、角色、异常、流程；表单页单独提取 page-global（准入、提交边界、返回、未保存离开）。
   - 不脑补 PRD 未写的通用组件行为。
   - **出口**：页面级需求清单。**证据**：引用的 PRD 章节列表。

3. **DOM target inventory**
   - 稳定模块级目标；记录 label、selector 候选、路径、可见性。
   - Modal/drawer/tab：记录展开操作，在可见后核对锚点；状态块配 `scopeLabel`（§2.2.2）。
   - **出口**：每页模块表（含隐藏态）。**证据**：关键 `data-anno` 或 selector 与 §2.2 一致。

4. **Aggregate by UI module**
   - 一模块一角标；filter/table/tabs/form/modal/drawer/field group/batch 典型。
   - 跨区规则集中一个 `page-global`（无 selector）；纯展示页无源规则则不强加。
   - **出口**：模块与块映射草稿。**证据**：§5.2 范围判断（N 标 / M 不标及理由）。

5. **Write annotation Markdown**
   - 目录见 §3.2；每块 `来源：` 与 `sourceRefs`；不改业务 PRD。
   - 仅用户明确要求时建 `changelog.md`。
   - **出口**：`annotations/**/*.md`。**证据**：块与 PRD 来源可追溯。

6. **Write `annotation.config.json` / workspace**
   - `scope`（kebab-case）、`page` / `routeMatcher`、`screenState`、`target`、`markdownFile`、`blockId`、`type`、`scopeLabel`（状态块）；块 `id` 见 `STANDARD.md` §5。
   - 单 runtime 用 `annotation.workspace.json`（§2.4），禁止手工合并多份 config。
   - **出口**：config + workspace。**证据**：config 条数与 md 块一致。

7. **Compile and validate**
   - 执行 §7.1 三道命令（含 coverage 时按项目 manifest 传 `--output` / `--coverage`）。
   - 存在 unmapped requirements、缺块、缺 selector、编译失败 → **停止**。
   - **出口**：绿色 compile + check + build。**证据**：§7.1 命令原始输出。

8. **Install runtime（最小侵入）**
   - `scripts/install_annotation_kit.py` 或按 `references/integration-patterns.md` 注入；不替换用户已有配置除非明确要求。
   - **出口**：`annotation-kit` 在 public/静态目录且 HTML 已引用。**证据**：入口文件中的 script/link。

9. **Browser verification**
   - Badges：overlay 定位，不改布局；`initialMode` 默认 `preview`。
   - 隐藏模块：未展开无角标，展开后角标位置正确；`scopeLabel` /「需操作后查看」符合 §2.2.2。
   - 面板：§8.1 交互流；弹窗只读、可拖放、事件隔离；Markdown 表格/列表正常；切换模式有 toast；refresh 无缓存读 bundle。
   - **出口**：评审可走完「入口 → 角标 → 详情」。**证据**：无控制台错误；§7.2 运行层勾选。

### 4.2 Workflow B：增量更新

1. Diff PRD、页面、annotations、config。
2. 分类：added / modified / deleted / moved。
3. 只改受影响 md 块与 selector/`page`/`routeMatcher`/`scopeLabel`；字段约束与 `来源` / `sourceRefs` 对齐当前 PRD；page-global 集中跨字段规则。
4. 除非用户要求，不改 runtime 样式与徽章形态。
5. 仅当模块或需求真删除时移除角标。
6. 保留补充标注 id（§6.3）。
7. 重跑 §7.1，再浏览器验证（同 §4.1 第 9 步）。
   - **出口**：变更块列表 + 全绿 §7.1。**证据**：命令输出与浏览器抽检。

### 4.3 迭代切换与上线后下线（操作）

**新迭代开始**

- 新建本迭代 `annotations/` 与 config；编译**覆盖**原型 bundle，不吃上一轮残留。

**本迭代上线后**

1. 原型 `public/annotation-kit/annotation.bundle.json` 中 `annotations` → `[]`（runtime 与业务代码不动）。
2. 原型目录 `npm run build` 并随发版部署；§7.1 中 `index.html` 缓存版本见 §7.1。
3. PRD 侧 annotations 源文件**留档不删**，不再部署到原型。

## 5. 写什么、写多少（范围与内容形态）

### 5.1 业务语言与读者（Annotation Language Standard）

读者是**业务方与评审**，不是开发：

- 页面用面包屑/页面名，不以 URL 作主描述。
- 状态/枚举用中文业务名，英文仅括号辅助。
- 规则用业务语言；字段用界面中文标签。
- 主描述为英文枚举或技术路由的块不合规，须改写。

### 5.2 标 / 不标

执行前应用 `references/annotation-scope.md`，在交付中输出 **「N 处标注 / M 处不标及理由」**。SKILL 不在此重复范围表。

### 5.3 字段·区域·整页三层与 `page-global`

1. **字段级**：单字段必填、格式、范围、精度、默认、唯一、校验时机。
2. **区域级**：表单区内联动、条件必填、共同校验；普通字段合并为 `field` 块，不逐字段角标。
3. **整页级**：准入、防重提交、未保存离开、失败重试、返回；`type=page-global`，无 selector，不挂按钮角标。

区域聚合不删字段说明：有 TSV 则 13 列 Excel 表（字段所属分组 / 字段名称 / 字段类型 / 字段来源 / 字段说明 / 必填性 / 新增页 / 编辑页 / 列表展示 / 可筛选 / 详情展示 / 取值说明 / 备注），忠于 TSV、无值填 `-`、表下写来源；无 TSV 用四列表（字段 | 展示/输入类型 | 业务说明 | 约束与备注）并标「待补字段清单 TSV」。字段事实以 TSV 为准，跨字段以 PRD 为准，交互以 Demo 为准；冲突写待确认。`page-global` 须在 config 保留 `page` 与 md 映射；编译器生成空 target，runtime 用 `isPageGlobal` 定位。

### 5.4 块内结构与六 Tab + `type` 分类

**Type**（面板筛选，每块一个）：`page` | `page-global` | `interaction` | `rule` | `field` | `pending`。

**块内正文**：`需求描述` → `来源` → 分组标题 → `- 项名：描述` 列表，禁长段堆砌。

**详情六 Tab**（每块齐全，空 Tab 也展示）：`全部` | `页面内容` | `交互说明` | `业务规则` | `字段说明` | `待确认`。`page-global` 在「页面」Tab 分组展示且保留 runtime 类型。

### 5.5 编写与 config 映射（延伸阅读）

抽取清单、聚合规则、Markdown 块模板、Mermaid 用法、补充标注 `A*`、多 PRD 目录示例 → **`references/annotation-authoring.md`**。生成或更新标注前必读。

## 6. 技术映射（config / 选择器 / 标识）

### 6.1 `annotation.config.json` 字段职责

| 字段 | 用途 |
| --- | --- |
| `scope` | 模块命名空间；导出键 `scope:id` |
| `id` | 角标数字；规则见 `STANDARD.md` §5 |
| `page` | 代表性真实路由 |
| `routeMatcher` | 同页等价路由正则 |
| `scopeLabel` | 状态层绿色标签（弹窗/页签等） |
| `type` | 面板类型筛选（§5.4） |
| `moduleName` | 面板标题 |
| `target.selector` | DOM 锚点；`page-global` 无有效 selector |
| `markdownFile` / `blockId` | 对应 md 块 |
| `sourceRefs` | 覆盖 `sourceRequirements` |
| `sourceRequirements` | 声明需映射的需求 id |

每条 annotation 映射一条 md 块；同文件可多块。`annotation.workspace.json` 声明 `inputs`（§2.4）、`output`、可选 `coverage` / `htmlOutput`。

### 6.2 Selector Rules 与低侵入策略

**选择器优先级**：`data-anno` → `data-testid` / `id` / `aria-label` / `name` / `role` → 语义+文案 → class → 生成路径（临时）。

不稳定则模块根加 `data-anno="module-xxx"`。不改 UI 结构、不耦合业务 state。

**集成模式**（栈细节 → `references/integration-patterns.md`）：

1. 不能改源码：bookmarklet / 注入。
2. 一行 runtime：拷贝 `annotation-kit` + entry 引 css/js。
3. Selector hint：仅加 `data-anno`。
4. 组件集成：仅当 DOM 选择器不可靠。

修改新项目类型前读 integration-patterns；协作部署读 collaboration-deployment。

### 6.3 显示 id 与补充 id

- 常规块 id：见 `STANDARD.md` §5（按 `screenState` 分组连续编号）。
- 补充标注：`A1`、`A2`、`A3`（同等对待，导出含在内）。
- 与用户明确要求时可用 `1a`/`1b` 表示从属关系。

### 6.4 Mermaid

可选： fenced `mermaid`；复用 `window.mermaid` 或 config 的 `mermaid.src`；不可用则源码块展示；默认不依赖外网 CDN，离线用本地 mermaid 资产。

## 7. 集成与发版（必做门禁）

### 7.1 发版前三道命令与缓存版本

在业务项目根（例：`/Users/liulongfei/个人文件/WorkSpace/vivo/cms-project`）**依次执行，全绿才算验收**：

```bash
python3 <PMLOPHY_SKILLS_PATH>/skills/prototype-annotation/scripts/compile_annotations.py "03-产品设计/私域2.0一期/04-评审PRD/annotations/annotation.workspace.json"

python3 <PMLOPHY_SKILLS_PATH>/skills/prototype-annotation/scripts/check_annotation_assets.py 99-产品原型prototype/public/annotation-kit --src 99-产品原型prototype/src --routes 99-产品原型prototype/src/App.tsx

cd 99-产品原型prototype && npm run build
```

`check` 额外拦截三类静默失败：(1) 锚点在 `--src` 中不存在；(2) `page` / `routeMatcher` 命不中真实路由（不含 `*` / `/*` 兜底）或只命中重定向、`routeMatcher` 过窄未覆盖本块 `page`；(3) 同一 `screenState` 下角标 `id` 重复或未从 1 连续。仅 compile、不加 `--src`/`--routes` **不算交付**。

每次发版标注或更新 runtime：递增 `index.html` 中 `runtime.css`、`override.css`、`runtime.js` 的 `?v=`（格式 `v=YYYYMMDDx`）。**不递增会被 CDN（如 Cloudflare）长期缓存旧文件**，用户看不到新角标/面板行为。

### 7.2 四层校验走查

每次交付记录四层证据：

1. **来源层**：内容可追溯 PRD/字段清单/评审记录，无他项目事实。
2. **结构层**：块 `id` / `screenState` 符合 `STANDARD.md` §5 与 §5.3；`sourceRefs` 覆盖 source requirements。
3. **资产层**：bundle 内联 md、target 完整、coverage 无未映射；表头与数据行计入 coverage，分隔行不计。
4. **运行层**：route、徽章、面板、六 Tab、表格、定位、滚动、只读边界；控制台无错。

### 7.3 交付前检阅清单

| 检查项 | 做法 |
| --- | --- |
| 条数一致 | 角标数 = config 块数 = bundle 条数 |
| 同屏状态内无重号 | 见 `STANDARD.md` §5 |
| 需操作区域 | 有 `scopeLabel`；无角标但面板「需操作后查看」属预期 |
| 旧迭代已下线 | bundle 无残留；上线后 `annotations: []` 已 build |
| 路由未漂移 | `page` / `routeMatcher` 与路由表一致 |
| 缓存版本 | `index.html` 三处 `?v=` 已递增 |

### 7.4 Agent 交付证据（Tooling + Validation）

交付回复须含：

1. **Scope**：§5.2 的 N/M 判断。
2. **§7.1**：三道命令与 build 的**真实终端输出**（全绿）。
3. **Browser**：角标、`scopeLabel`、需操作场景、点击详情、无 JS 错误。

终检勾选：

- 已确认 initialization 或 update；未污染业务 PRD。
- 当前迭代 bundle 仅本迭代标注；每块有 `来源` 与 `sourceRefs`。
- 表单跨字段有 `page-global`；无冗余同模块角标。
- Runtime 注入最小化；workspace 编译，禁止手搓合并 config；禁止 bundle 回灌 input。
- 徽章不改布局；`runtime.zIndexBase` 处理叠层；弹窗可开/关/拖/缩放/导出且事件隔离。
- 无编辑控件/写回 API；refresh 重读 bundle。
- `page` 真实、`routeMatcher` 合法、无伪造子路由；静态单页可用 `page: "*"`。
- 可选 htmlOutput 为渲染后 Markdown；md 预览支持表/列表/任务/标题等。
- 若未跑 build/浏览器，须说明原因。

## 8. Runtime 行为标准（评审体验）

### 8.1 面板与交互流

- 流程：「原型标注」入口（白底文档图标）→ 切换标注模式 → **先出编号角标**（非直接出全文）→ 点角标出内容并高亮区域 → 侧栏项可定位。
- 默认 `preview`：加载不直接展示标注正文。
- 入口「标注清单」「原型标注」：**浮动可拖**，不占布局、不挡操作；`sessionStorage` 记位置。
- **双入口激活态对称（2026-08 踩坑）**：两个入口分别点开时，**被点中的那个按钮自身**都必须呈现选中/高亮激活态，且两者激活态视觉一致；只让一个亮、另一个不亮 = 半修。**根因**：JS 切换状态 class（如 `is-active`）不等于界面生效，须有 CSS 规则与 class 成对。排查「按钮不亮」：先在 runtime 里确认该按钮 toggle 了状态 class，再在样式表里确认有对应激活态；两样缺一即未完成，两样都在后再查缓存/部署。**验收**：点「标注清单」看该按钮是否高亮 → 点「原型标注」同样 → 对比两者激活态是否一致。
- 面板：白卡片、标题+总数+关闭、「点击条目定位…」；Tab：全部/页面/交互/规则/字段/待确认（品牌绿高亮）；卡片含序号、类型、摘要、展开详情；点击定位 `data-anno`。
- **CRITICAL**：点入口必须先出角标再出正文，不是简单弹窗直接展示全文。
- 展开详情：分组规则 + 可折叠长文；样式白卡阴影圆角、品牌绿强调、干净滚动条。

### 8.2 待确认（Pending-Items）

非 PRD 抽取，是**人工评审问题跟踪**。

**模型**：id（块 key+时间戳）、description、source、status、resolution。

**要求**：每块待确认可录入；全局 Tab 聚合；`localStorage` 持久化（key：项目+页面+annotation key）；解决须填「解决方法」；浏览器不写 PRD 文件。

**导出待办**（全局示例，按块序号+标题分组）：

```md
## 待办项
### 序号 1（本模块列表页面）
- [ ] 问题描述
  - 解决方法：（待补充）
- [x] 已解决问题
  - 解决方法：...
```

单块导出：仅该块问题，仍含 `## 待办项` 与 `### 序号 X（块标题）`。Golden rule：待确认 = 人工录入，不从 PRD 自动抽取。

待确认列表须可滚动（`overflow-y`+max-height），且不在自身 scroll 里重建 DOM。

### 8.3 拖拽与点击共存

- **禁止**在拖容器上用 `setPointerCapture`（会导致子按钮点不了）。
- `pointerdown` 在把手，move/up 在 `window`；小位移放行 click，大位移拖动并抑制一次误触。
- 浮层与按钮 `pointer-events: auto`；`.vpa-root` 为 `pointer-events: none`；工具栏 z-index 高于面板。
- 验收：点按钮有效；拖动能移；拖后再点仍有效。

### 8.4 面板 Tab 状态持久化

滚动触发 `scheduleMeasure` 重建 panel 时，详情 Tab 不得丢。用 `VPA_STATE.detailTabByCard`（`data-annotation-key`）在 DOM 外存 Tab；切换时写入，重建时恢复：

```js
const cardKey = container.closest('[data-annotation-key]')?.dataset.annotationKey;
const savedTab = cardKey ? VPA_STATE.detailTabByCard.get(cardKey) : null;
const requestedTab = savedTab || container.dataset.detailTab || initialTab;
if (cardKey) VPA_STATE.detailTabByCard.set(cardKey, currentTab);
```

验收：选「页面内容」后滚动仍保持。

### 8.5 滚动不得重建可滚动容器

滚动时只 `measureBadges()`，**禁止**在 scroll 回调里 `renderAnnotationPanel()`。Panel 重建仅由 Tab 切换、展开、数据刷新触发：

```js
window.requestAnimationFrame(() => {
  VPA_STATE.measureScheduled = false;
  measureBadges();
  // never call renderAnnotationPanel() during scroll
});
```

验收：列表 `scrollTop` 保持；详情横滑 Tab 仍可用。

## 9. 只读边界与安全

Runtime 只读展示：本地改 md/config；发布走正常 Git/部署；浏览器读 bundle、渲染、导出。

禁止：`contenteditable`、Markdown 编辑器、draft、`saveEndpoint`、鉴权写 API。Export 是只读交付，不是编辑流。

协作/云/团队流程与安全边界见 `references/collaboration-deployment.md`。

## 10. Bundled 资源与延伸阅读

**资产与脚本**

- `assets/annotation-kit/runtime.js` / `runtime.css`
- `assets/annotation-kit/annotation.config.json`、`annotation.schema.json`
- `assets/annotation-kit/annotation.workspace.json`、`annotation.workspace.schema.json`
- `scripts/compile_annotations.py`、`check_annotation_assets.py`、`install_annotation_kit.py`

**阅读顺序**

1. `references/annotation-authoring.md` — 写标注与 md/config 细节  
2. `references/annotation-scope.md` — 标不标  
3. `references/integration-patterns.md` — 各技术栈接入  
4. `references/collaboration-deployment.md` — 部署与协作  
