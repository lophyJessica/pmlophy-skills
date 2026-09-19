# Lophy Skills

路飞个人 AI 工作流 Skill 集合。

## 当前 Skill

### `pm-to-questionnaire`

把“我缺少某个人掌握的事实或决策信息”转化为可发给对方填写的结构化问卷，适用于业务调研、入职摸底、跨团队沟通和访谈准备。

特点：

- 只追问问卷的发送对象和信息缺口，不把用户拖进无休止的主题拷问；
- 能查到的事实优先由 Agent 自己查，不让用户重复向别人询问；
- 默认先在对话中生成草稿，用户明确要求保存时才写文件；
- 优先生成 5～10 个关键问题；
- 适配业务负责人、技术负责人、同事、客户、供应商等不同收件人；
- 每道题只问一个核心事实或决策，支持异步填写和当面访谈。

### `pm-discovery-dialogue`

把“业务提出的功能答案”还原为真实问题，并在关键事实掌握于他人时生成信息缺口问卷。

它合并了：

- 双向钢人访谈：现状、痛点、影响、不做后果、决策变量、最小动作；
- `to-questionnaire`：收件人、信息缺口、5～10 个高价值问题、异步填写模板。

适用于业务调研、入职摸底、需求确认、跨团队沟通和需求变更评估。默认先在对话中输出问卷草稿，不擅自写文件；Forge 项目遵循 `context/ > templates/ > prd-docs/`。

### `pm-handoff`

把当前任务压缩成可移交给新会话、Codex、Workbuddy、Cursor 或同事的便携交接文档。只保留任务目标、已确认状态、完成证据、未完成项、下一步责任人和约束，不重复长会话内容。

### `pm-research`

基于官方文档、源码、发布说明、真实 API 或系统输出完成事实调研，区分已确认事实、推断、不确定性和建议。适合工具、模型、套餐、API、政策和当前系统状态查询。

### `pm-to-spec`

把已经讨论并拍板的产品决定整理成 Agent 可执行规格，不重新拷问用户。明确问题、目标、修改层、保留层、范围、红线、验收标准、执行位置和交付责任。

### `pm-prototype-decision`

用一次性、可丢弃的原型回答一个具体产品问题，例如 UI 方向、业务流程、状态机或信息架构，再把验证结论交给正式实现。

### `prototype-annotation`

面向已有 React、Vue 或静态 HTML 原型的业务原型标注 Skill（**v2.1**），包含标注方法论、runtime、编译工具与校验脚本。亮点：三级标注体系（区域级 / 页面级 / 本页规则 page-global）、字段说明**优先从字段清单详细稿 TSV 生成 13 列 Excel 表**（无 TSV 模块退化 4 列并标"待补字段清单 TSV"）、每次交付过四层校验（`check_annotation_assets.py`）、标注清单 / 交互流 / 6 Tab 详情 / 点击拖拽共存等规范。

### `prd-backfill`

前端/代码改动落地后把改动**回写 PRD 与关联文档**（字段清单、业务规则、Demo 页、流程图、验收清单、权限设计）的 Skill。含 改动类型 × 文档映射表、流程图回写要点（业务流程 vs 系统流程）、检查清单与红线（忠实已实现、单一事实源、最小改动、联动一致）。forge 项目常用 `prd-docs/modules/<模块>/` 套件文档。

### `prd-requirement-review`

对已有 PRD/方案做**两档需求评审**（简档·3-5 分钟快速 / 全档·标准评审报告），输出 S0-S3 分级、阻塞/风险/待确认事项、以及"能否进研发"结论。含 7 视角→维度速查、Given/When/Then 可验收性、简档模板+示例、报告头骨架与交付前自检清单。

### `de-ai-tone`

中文长文**去 AI 味**自检（基于 283 万字语料实测的 11 条白名单规则，每条带触发标记）。白名单式改写：只改命中规则的句子，未命中逐字保留；信息守恒（数字/日期/引语/来源不增删）、框架不动、不强加人称口语。含"别改清单"（句长/虚词/比喻/被动等实测站不住的特征）与交付验收。

### `a2a-instruction-format`

**给 Codex/反重力/Cursor 等编码 agent 写五段式指令的规范**（Context/Request/Output format/红线禁止/Checkpoint）。含 **Skill 路由：先扫后用**（写指令前先扫 skill 库命中就引用、防 skill 变摆设）、agent 分工（文本产物 vs 前端用 IDE）、执行环境路径（Mac 源码/VPS 部署）、硬门禁（单代码块、不打断运行中 agent、全仓保留层等）。深入案例 references 留 Hermes 内部。

### `structured-ai-prompt-template`

**五段式结构化提示词模板**（用户偏好的 Context/Request/Output format/红线禁止/Checkpoint 版），配合给各 agent 的指令生成。

### `product-manager-workflows`

通用 **PM 交付物技能**（给 Codex 写 PRD / 用户故事 / 验收标准 / MVP / 竞品分析 / 路线图 / 交接规格），带 prd / story-acceptance / research-analysis 三个模板。覆盖面宽而通用，与你自建 pm-\* 方法论有重叠；收编自 Codex 本地，作单一真源里的通用备选。

### `prototype-annotation-review`

**原型标注检阅**（评审那一侧）——与 authoring 版 `prototype-annotation` 配套：标注的检阅规范、本页规则 page-global、四层校验走查、tab 持久化/滚动不重建等九规范。负责"审"已有标注对不对、缺不缺。

### `old-system-ui-clone`（原版 · 维他命）

**老系统 UI 复刻**——上游忠实版（来自维他命 agent-skills），方法完整保留供回溯/与上游 diff。证据优先：先采源证据（截图/CDP/DOM 探针/Page Map/设计 token）再实现，结构断言只信证据、不靠 vision 猜；含四道硬门禁（证据先于代码/结构先于样式/视觉门禁=源vs克隆截图对比/降级标注）、工作流状态分级、QA 对比、design-system 沉淀。**日常用请走办公适配版 `old-system-ui-clone-office`**，本版留作上游参照。

### `old-system-ui-clone-office`（办公适配版·本用户用）

在原版老系统复刻方法上，**采集车头固定为 Cursor 内置浏览器**——本用户办公机/工作场景里所有 URL 都能用它打开、登录、持久登录态，是源系统证据首选入口（截图 + DOM 结构 + 登录态页面，证据可信可回溯）。适用于办公机复刻 CMS/生成环境/测试环境。四道硬门禁、QA 对比、design-system 沉淀等与原版一致；CDP/Playwright 脚本仅在能驱动浏览器时用，登录态页不走 Playwright 猜登录。

## AI Coding Skills（`skills/ai-coding/`）

5 个 AI Coding Skill，用于给 Codex / 反重力 / Cursor 等编码 agent 更稳的工作流。来自上游开源仓库（grill-me / react-best-practices / taste-review / simplify / test-desktop-app），test-desktop-app 按用户笔记自建为通用版。

| Skill | 时机 | 一句话 |
|---|---|---|
| `/grill-me` | 开工前 | 需求模糊？先问清楚再动手 |
| `/react-best-practices` | 组件写完后 | 组件别扭？按 Vercel 最佳实践体检 |
| `/taste-review` | UI 完成后 | 不好看？补一层审美审查 |
| `/simplify` | 提交前 | 代码太绕？删冗余、去过度设计 |
| `/test-desktop-app` | 打包后 | 没真跑过？端到端验证跑通才算数 |

工作流闭环：想清楚 → 做好设计 → 写对代码 → 删除冗余 → 实际验证。

## 使用边界

这些 Skill 是可复用的方法、工具和模板，不是完整业务应用。使用者需要自行提供项目代码、业务资料、PRD、数据和构建环境。

各 Skill 的具体使用说明见对应目录中的 `SKILL.md`。
