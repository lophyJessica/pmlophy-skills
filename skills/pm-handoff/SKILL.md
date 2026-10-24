---
name: pm-handoff
description: 当要把当前任务压缩成一份可携带的交接，让新会话、换模型、换 agent 或换协作人都能接着干、不用重放整段对话时用。
version: 1.0.0
author: Lophy / Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [handoff, session, context, agents, token-efficiency]
    related_skills: [pm-research, pm-to-spec, pm-discovery-dialogue]
---

# PM 交接

## 概述

在会话过长、工作要交给其他 agent，或协作者需要从已知状态继续时，生成一份紧凑、可携带的交接。交接是指针地图，不是对话实录：引用既有文件、报告、提交、URL 与产物，不要重复粘贴其全文。

## 何时使用

在以下情况使用：

- 应在上下文成本升高前结束长会话；
- 工作从 Hermes 转到 Codex、Workbuddy、Cursor 或其他会话；
- 任务在调研、实现、测试与部署之间暂停；
- 协作者需要当前状态与明确的下一步；
- 用户要求会话交接或续作简报。

以下情况不要使用：任务已完成且无需继续，或简短直接回复即可。

## 交接应包含的内容

只写下一执行者需要的信息：

1. **任务目标** — 要达成的结果。
2. **当前状态** — 已确认事实，而非猜测。
3. **已完成工作** — 简明要点，附路径、URL、提交 ID 或报告名。
4. **未完成工作** — 未完成项及其阻塞。
5. **下一步** — 一条可执行的下一步，含执行者与位置。
6. **约束** — 范围、红线、用户已定决策、勿重复事项。
7. **建议加载的 skill** — 下一执行者应加载的 skill。
8. **证据地图** — 指向权威源文件、报告、构建或部署的指针。

## 规则

- 不要重放整段对话。
- 不要把未核实的 agent 说法写成已确认事实。
- 区分「已上传」「已部署」「HTTP 200」「用户已验收」「已提交/已推送」。
- 脱敏密码、API 密钥、令牌、个人隐私与敏感端点。
- 不要编造缺失状态；写「未知」或「待核实」。
- 保留用户的语言、决策与范围边界。
- 若下一环节是新会话，须明确说明；当前上下文仍必需时，不要推荐 `/new`。

## 输出方式

### 对话内

默认：在对话中用简明 Markdown 内联输出交接。除非用户要求，不要创建文件。

### 文件交接

用户要求保存时，写到临时或用户指定位置，不要自动写入项目根目录。使用描述性文件名，如 `handoff-<topic>-<date>.md`。确认文件存在并报告绝对路径。

## 模板

```markdown
# Handoff: <topic>

## Mission
<desired outcome>

## Confirmed state
- <fact + source>

## Completed
- <action> — <artifact/path/URL/commit>

## Open work
- <unfinished item> — <blocker or next decision>

## Next action
**Owner:** <person/agent>
**Where:** <machine/repository/path>
**Do:** <one executable next step>

## Constraints and do-not-repeat
- <scope/red line>

## Suggested skills
- <skill name> — <why>

## Evidence map
- <pointer>
```

## 验收清单

- [ ] 任务目标一段话说清。
- [ ] 每条已完成陈述有指针，或标为用户已确认。
- [ ] 未完成项与下一负责人明确。
- [ ] 无敏感值、无重复粘贴长产物。
- [ ] 交接比其所替代的上下文更短。
