---
name: pm-to-spec
description: 当要把已经讨论定案的产品决策，转成 agent 可直接执行的实现规格时用，不重开已定的问题。
version: 1.0.0
author: Lophy / Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [product-spec, agent-instructions, scope, acceptance, handoff]
    related_skills: [pm-discovery-dialogue, pm-handoff, pm-research]
---

# PM 转规格

## 概述

把对话、已确认的调研结果或已批准的产品决策，压缩成 Codex、Workbuddy、Cursor 或其他执行 agent 可行动的规格。这是综合整理，不是再次访谈。

## 何时使用

在以下情况使用：

- 用户已讨论并确认目标；
- 调研结论需要变成可执行工作；
- 任务须交给外部编码 agent；
- 大请求需要清晰的范围、保留层与验收门禁。

关键产品决策未定时不要用；先用 `pm-discovery-dialogue`。琐碎的一行指令不要用本 skill。

## 流程

1. **阅读源对话与产物** — 不要重复追问已知信息。
2. **从用户视角陈述问题。**
3. **定义期望结果与用户可见行为。**
4. **区分变更层与保留层。**
5. **列出范围与明确的范围外项。**
6. **写约束、红线、依赖与数据模型限制。**
7. **先定义外部可验证行为，再写构建/测试与交付证据。**
8. **写明负责人、机器、仓库、分支与部署责任。**

若发现矛盾，停止综合并呈现矛盾，不要静默选边。

## 规格模板

```markdown
# <Task title>

## Problem
<what is wrong or missing from the user's perspective>

## Outcome
<what should be true after completion>

## Context and evidence
- <confirmed fact + source path/URL/report>

## Scope
### Change
- <pages/modules/files or user-visible behavior>

### Preserve
- <business logic, data, routes, integrations, anchors, existing work>

### Out of scope
- <explicitly excluded work>

## Decisions and constraints
- <confirmed product decision>
- <data-model or technical constraint>
- <red line>

## Execution request
1. <direct action>
2. <implementation detail>
3. <regression checks>

## Acceptance gates
- <user-visible behavior>
- <build/test result>
- <artifact or deployment evidence>

## Delivery
- Owner: <agent/person>
- Where: <machine/repository/branch>
- Commit/push: <allowed or forbidden>
- Upload/deploy: <who does what>
```

## Agent 交付规则

代码类任务，实际指令须以直接执行句开头：修改既有项目，不要把指令存成文档，不要只输出计划。

须包含：

- 编辑前 `git pull --ff-only`；
- 确切项目路径与目标范围；
- 须保留的既有工作；
- 构建命令；
- 需要打包时的唯一 ZIP 名与「解压即根」结构；
- 项目流水线需要时的完整可复制上传命令；
- 上传与部署的明确负责人；
- 无独立核实不要声称已部署。

在事实可得时，不要让 agent 推断项目路径、参考页、数据契约或验收标准。

## Forge 适配

Forge 项目：

```text
context/ > templates/ > prd-docs/
```

- 以 `context/` 为业务权威来源；
- 用 `templates/` 作文档结构；
- 将 `prd-docs/` 视为生成输出；
- 除非明确在变更范围内，保留 Dexie schema、API 契约、路由结构、既有标注锚点与用户改动；
- 区分本地构建、传入上传、人工部署与用户浏览器验收；
- 不要仅凭 HTTP 200 就当作新部署已生效。

## 验收清单

- [ ] 规格综合已确认决策，不重开已定问题。
- [ ] 问题、结果、范围、保留层与范围外明确。
- [ ] 重要主张有来源，或标为假设。
- [ ] Agent 路径、负责人、分支、构建、交付与验收明确。
- [ ] 规格足够小，所选 agent 能可靠执行。
