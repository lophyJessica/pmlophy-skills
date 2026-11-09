---
name: pm-ai-project-setup
description: "Set up an AI-assisted PM project workspace — standard directory structure, AGENTS.md, context files, and the 三层六步工作流 methodology for structured AI collaboration."
version: 1.0.0
author: Hermes Agent
tags: [pm, product-manager, ai-collaboration, project-setup, agents.md, context]
---

# PM AI Project Setup

Build a structured project workspace that maximizes AI output quality by systematically organizing business context, rules, and templates. Based on PM Vitamin's "三层六步工作流" methodology.

## Trigger

- User asks to "搭项目结构" / "建项目目录" / "setup project for AI"
- User wants to apply PM Vitamin course methodology to a real project
- User says "帮我建 AGENTS.md" or "写项目上下文"

## The Core Formula

```
AI输出质量 = 上下文质量 × 提示词质量
```

Same model, same prompts — context quality is the differentiator. This skill builds the "上下文质量" half.

## Step 1: Create Directory Structure

Use this standard layout (from PM Vitamin course):

```
project-name/
├── AGENTS.md              ← AI's "onboarding guide" — must be in root
├── CLAUDE.md              ← Pointer to AGENTS.md (for Claude Code compatibility)
├── context/               ← AI's knowledge base (markdown, plain text)
│   ├── 00-背景信息索引.md  ← File map: what exists, what's planned
│   ├── 01-项目背景.md      ← Business context, project origin, scope
│   ├── 02-上下游关联系统.md ← System landscape and data flows
│   ├── 03-主要功能模块.md   ← Module map and feature inventory
│   └── ...                ← Add more as the project grows
├── template/              ← Reusable skeletons (PRD, field list templates)
├── prompt/                ← Battle-tested prompts (copy-paste into chat)
├── prd/                   ← PRD workspace (organized by business module)
│   └── <module-name>/
├── prototypes/            ← Frontend prototypes (one subdir per feature)
├── drafts/                ← Temporary drafts, chat exports, unclassified
└── reference/             ← Human-only: old PRDs, screenshots, meeting notes
```

**Key rules:**
- `context/` is AI-input: domain knowledge, cross-module rules
- `prd/` and `prototypes/` are AI-output: where AI writes files
- `drafts/` is temporary; `prd/` is organized deliverables
- `reference/` is human-only — distill into `context/` before feeding to AI

## Step 2: Write AGENTS.md

This is the AI's first read on every session. Template:

```markdown
# <Project Name>

> 项目类型 | 角色 | 周期

## 项目简介
<2-4 sentences: what this project is, what problem it solves>

## 重要文件
- 业务上下文：`context/`
- 输出模板：`template/`
- 常用提示词：`prompt/`
- PRD 工作区：`prd/`
- 原型工作区：`prototypes/`

## 工作规范
- 所有产出文档统一使用 Markdown 格式
- PRD 中的字段名使用中文显示名，必要时加注数据库字段名
- 如有不确定的业务规则，请先标注【待确认】而不是自行假设
- <add project-specific conventions>

## 约束（NIS：Not In Scope）
- <what this project explicitly does NOT cover>
- <boundaries that prevent scope creep>

## 技术栈
- 前端：<stack>
- 后端：<stack>
- 数据库：<stack>

## 相关系统
| 系统 | 关系 | 说明 |
|------|------|------|
| <system> | 上游/下游 | <what data flows between them> |
```

**Verification:** After writing, ask AI "介绍一下这个项目". If the answer reflects AGENTS.md content → working. If not → check file location/name.

## Step 3: Write CLAUDE.md (pointer only)

For Claude Code compatibility, create a minimal `CLAUDE.md` that redirects to AGENTS.md:

```markdown
# 项目规则入口

所有项目规则、工作流规范、目录结构、命名约定等，统一维护在 `AGENTS.md`。

**Claude Code 操作须知：**
- 读取项目规则 → 读 `AGENTS.md`
- 新增或更新规则 → 写入 `AGENTS.md`，不要写到本文件
- 本文件仅作入口索引，保持最简，不存实质内容
```

## Field Lists Use TSV (Mandatory — PM Vitamin 实战篇)

Maintain field lists (字段清单) as **TSV**, NOT Markdown tables and NOT Excel. Rationale: pure text (AI can read/write), better than md tables when fields are many, and leverages AI IDE autocomplete (Cursor TSV plugin).

**Two-version method:**
- 初稿 (5 cols): 字段所属分组 | 字段名称 | 字段类型 | 字段来源 | 字段说明/描述 — confirm "有哪些字段"
- 详细稿 (13 cols): + 必填性 | 新增页 | 编辑页 | 列表展示 | 可筛选 | 详情展示 + 取值说明 | 备注 — define "字段怎么表现"
- **详细稿确认后 = 字段唯一事实源**; 初稿 becomes process record, no longer updated.
- **Keep ONLY TSV, never a md copy** — a `.tsv` + `.md` pair both editable creates "which is latest" chaos.

**Three-layer split (field fact vs business rule vs page interaction):** 字段事实进 TSV, 业务约束进业务PRD, 页面交互进 Demo PRD. E.g. "采购数量": TSV says 整数/>0; 业务PRD says 提交审核时每明细行必填/审核后不可改; Demo PRD says 用 NumberInput/失焦校验/错误定位到明细行.

Full detail + 6-step enrichment + version-directory iteration: see `references/tsv-field-list-methodology.md`.

## 需求池 / 台账类文档：状态是列，不是目录

凡是「一条记录 + 若干会变的属性（状态 / 优先级 / 版本 / 负责人）」，都用**一张 TSV 做唯一事实源**，不要按属性建文件夹。需求池、Bug 池、验收清单、待办台账同理。

**反面结构**（真实踩过）：`需求池/已上线/ 预研未排期/ 无版本/ V1.8.0/` 一堆状态目录，每个需求一个 md，外加一份上百行的手工索引 README。四个问题：

- **状态会变，一变就要搬家**：需求从「预研未排期」→「V1.8.0」→「已上线」要走三次 `git mv`，git 历史断、外部引用失效
- **语义混层**：版本号（V1.8.0）和状态（已上线）并列在同一层目录，两种口径混着
- **三重冗余**：同一个状态写在文件名后缀（`-P2-需求接受`）＋ 索引表一列 ＋ 文件夹名
- **索引靠手维护**：加一条需求要建文件、搬目录、再改 README 三处，迟早漂移

**正确结构**：

```
需求池/
├── README.md             只写规则（怎么加一条、每列含义），不列全表
├── 需求池-YYYYMMDD.tsv    唯一事实源：状态 / 优先级 / 版本 / 负责人全在这
└── 需求拆分/             针对大需求的深挖产物（md），不是需求池本身
```

- 要「已上线清单」= 筛 `需求状态 = 需求上线`，不需要一个装满几十个文件的文件夹
- 编号列沿用来源系统的行号或单据号，保证能和源头一眼对齐

**分清两类东西**——混在一起，目录就会显得「重」：

| | 是什么 | 形式 |
|---|---|---|
| 需求池 | 状态跟踪表，一行一条 | TSV |
| 需求分析产物 | 对某条需求深挖的方案 / 拆分 / PRD | md，单独目录 |

## 目录规范：不建游离目录，文档全部入编号体系

顶层只认 `00-草稿对话 / 01-全局背景信息 / 02-需求调研 / 03-产品设计 / 04-常用模版 / 05-提示词合集 / 06-产品方法论 / 07-UI规范库 / 08-相关资料 / 99-产品原型prototype`。一旦出现 `docs/` 这类游离目录，内容就会杂糅（架构图、OKR、培训材料、竞品调研、历史汇报躺在一起），找东西靠记忆。

**归位映射**（按内容属性，不按来源）：

| 内容 | 去哪 |
|---|---|
| 全景图 / 架构图 / 流程图 | `01-全局背景信息/flow/` |
| 对标调研、竞品截图、内外部系统调研 | `02-需求调研/<调研主题>/` |
| 未评审、未定稿的方案与设想 | `00-草稿对话/<需求线>/` |
| 已评审定稿的 PRD / 字段清单 / Demo PRD | `03-产品设计/<需求线>/` |
| OKR、汇报材料、培训材料、参考数据 | `08-相关资料/参考数据/<类别>/` |

判定「放 00 还是 03」只看一件事：**需求状态是否已过评审**。需求池里还是「需求提出 / 需求接受」、方案还有卡开发的待确认项 → 草稿；PRD 套件齐了、评审通过 → 03。

搬家一律 `git mv`，保留历史；搬完同步改 README 目录树与引用它的文档。

## 评审 / 对外文档：写得像给同事看的

交付物一旦要上评审或发给非技术同事，先过两道：

1. **人称用真名，不用昵称**。工作文档里出现个人代号，评审时无法对应到具体的人。全仓范围一次性替换（`grep -rc` 先统计），替换后复查零残留。
2. **agent 代号不进交付物**。版本记录 / 责任列里出现 agent 名字会引出「这是谁」的追问。写人名，或留 `—`；**只换署名，不删版本行**——版本行承载「哪版改了什么」，删了就丢历史。角色定义类文档（方法论、工作流）不删句，把代号换成角色名（如「个人 Agent（AI 指令官）」），否则句子失去主语。

方案 / 迭代计划 / 上线报告这类文档该配什么图、表格怎么承载结论、数字怎么核出处，见 `references/product-spec-doc-with-diagrams.md`。

## 删旧结构前的纪律（用户会盯着这一步）

1. `grep -rn` 全仓查引用——索引 README、模板说明、自检报告里常写着旧路径
2. 查别处有没有备份（横扫其他仓库/技能库同名标题），有备份才敢说「删了不丢」
3. 待删清单**逐条列给用户等确认**，不自作主张删
4. 用 `git rm` 不用 `rm`，留历史可回滚
5. **「删内容」≠ 删文件夹**。用户说目录里的东西「太冗余、全删了」，删的是里面的文件，目录结构保留；要连目录一起删必须单独确认。搞反一次就得重建目录+补 .gitkeep，且会让用户无法再信你的删除尺度
6. **优先存档不删**。用户常说「存档吧」——`git mv` 到 `_archive/旧版-<来源日期>/`，历史与文件都在，目录却清爽了
7. git 不跟踪空目录：确实要保留空壳时，每个空目录放一个 `.gitkeep`，否则 pull 下来目录会消失；反之决定连目录删掉时，把 `.gitkeep` 一并 `git rm`

## Step 4: Create Context Files

### 00-背景信息索引.md
A numbered file map. Format as a table:

| 编号 | 文件 | 内容 | 状态 | 最后更新 |
|:---:|------|------|:---:|------|
| 0 | `背景信息索引.md` | 本文件 | ✅ | date |
| 1 | `项目背景.md` | ... | ⬜ 待写 | - |

Mark files as ✅ (done), 🚧 (in progress), or ⬜ (planned). This index helps AI navigate the knowledge base.

### 01-项目背景.md
The "step ①" of 三层六步: business origin, pain points, target scope. Include:
- What existed before (external ERP? manual processes?)
- What specific problem triggered this project
- What's in scope for this phase
- What roles are involved

## Step 5: Know What's Already Available

Before starting, check what documents the user already has:
- Resume → project names, dates, technologies used
- Business process docs → existing flow diagrams
- Interview prep materials → narrative structures already written

**Don't rebuild what exists.** Extend, organize, and fill gaps.

## The 三层六步工作流 (Reference)

This is the methodology from PM Vitamin that this project structure serves:

| 层级 | 步骤 | 产出 |
|------|------|------|
| **宏观层** | ① 业务上下文 → ② 系统骨架 → ③ 场景粗流程推演 | 项目结构、背景、系统框架、业务流程 |
| **中观层** | ④ 字段清单+业务规则 → ⑤ 用例数据推演 | 字段定义、通用/具体业务规则、高频用例数据 |
| **微观层** | ⑥ 页面实现规格+前端原型 | 前端Demo PRD、原型代码 |

**核心原则：** 设计分层推进、每类信息只有一个权威源、PM做判断AI做传播。

## Pitfalls

- **Don't create files the user hasn't asked for yet.** The index maps what's planned (⬜), but actual files should be created as the user works through the methodology steps, not all at once.
- **重写用户自己写的文档时，只能重组结构，不能减信息。** 用户亲手写的方案里那些「设想场景表」「飞轮闭环」「分群静态/动态」往往是他思考的载体，你压缩成一句概括就是把它删了。重构后的篇幅应当大于等于原稿；“啰嗦”的是叙述方式，不是内容本身——把段落改表格、把机制画成图，而不是把条目合并掉。压缩完用户会直接问“那部分帮我补好了吗”。
- **AGENTS.md must be in project root**, not in a subdirectory. AI tools look for it at the top level.
- **CLAUDE.md must NOT duplicate AGENTS.md.** It's a pointer, not a second source of truth. Duplicated rules in both files WILL diverge.
- **context/ files should be under 2000 characters each.** If content grows, split into multiple numbered files. AI reads better with focused, smaller files.
- **Don't mix human reference material into context/.** Old PRDs, screenshots, and meeting notes go in `reference/`. Extract key insights from them before feeding to AI.
- **Verify after writing AGENTS.md.** The one-line test: ask AI "介绍一下这个项目" and check the answer.
- **Company attribution:** When filling project background from the user's real work history, cross-check which company each project belongs to against the resume. The user worked at 京东 (五星/爱导购/CRM/AI单据), 普元 (ERP/WMS/电商/智慧园区), and 尚强. Mixing these up (e.g., "京东做 WMS") is a critical error that would surface in interviews.
- **Practice/demo project ≠ the user's real project — keep them physically AND narratively separate.** When replicating the course demo (e.g. 强盛科技 进销存) to test the methodology, build it in a clearly-named sibling dir (e.g. `projects/qiangsheng-jxc-demo/`), NOT inside the real project. In the demo's AGENTS.md, state up top: "本项目为课程演示/练手，非真实交付；真实项目见 ../<real>/" and forbid cross-referencing business data. The user runs the demo alongside a real project (普元 WMS at `projects/puyuan-wms/`); mixing the two is the same 张冠李戴 risk as company attribution — fictional demo data must never leak into the real project and vice-versa.
- **Verify the demo's canonical scenario against the course source before scaffolding.** Don't assume which company/背景 a lesson used — lessons can differ (lesson 3 named 强盛科技; lesson 4's 进销存 demo did not re-name the company). If unsure, check the course's downloadable 演示文件 zip or the lesson doc first. Only the AGENTS.md 简介 + `context/01-项目背景.md` carry the company identity, so a wrong guess is a 5-minute fix — but confirm up front rather than build on the wrong source (the whole point is a权威源 that doesn't drift).
- **Directory naming drifts between course lessons — pick one set and stay consistent.** Lesson 3 uses singular `template/ prompt/ prd/ prototypes/`; lesson 4 uses `templates/ prompts/ prd-docs/ front-prototype/`. Adopt the set matching the workflow you'll actually run (use lesson-4 names if you'll run the PRD-suite → parallel modules → frontend pipeline), then don't rename mid-project.
