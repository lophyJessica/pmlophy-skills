---
name: pm-discovery-dialogue
description: Use when a PM needs to uncover missing business context, test whether a requested feature is a real need, prepare a stakeholder interview, or turn an information gap into an async questionnaire.
version: 1.0.0
author: Lophy / Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [product-management, discovery, interviews, questionnaires, steelman, requirements]
    related_skills: [prototype-annotation]
---

# PM Discovery Dialogue

## Overview

This skill combines two related PM practices:

1. **双向钢人访谈**：把业务提出的“功能答案”还原成真实问题，验证影响、优先级、反方风险和决策变量。
2. **信息缺口问卷**：当关键事实或决定掌握在另一位知情人手里时，把缺口整理成一份可异步填写或带进会议的问卷。

核心原则：先确认你缺的是什么，再选择“现场访谈”还是“问卷发送”。不为了显得严谨而把明确问题复杂化。

## When to Use

Use when:

- 业务说“要一个功能”，但问题、影响或优先级不清楚；
- 需要判断需求是真痛点、方案偏好还是伪需求；
- 准备立项访谈、需求确认会、变更评估或跨部门沟通；
- 用户缺少某位业务方、技术方、主管或客户掌握的关键事实；
- 对方无法马上开会，需要异步收集答案；
- 需要把一次访谈沉淀成可复用的业务结论。

Do not use when:

- 事实可以由 Agent 通过代码、文件、官方文档或系统状态直接查到；
- 用户已经给出完整范围、规则和验收标准，只需要执行；
- 只是机械整理、改名、批量替换或已明确的小修复；
- 用户已经明确拍板，不需要继续论证。

## First Decision: Interview or Questionnaire?

Choose the lightest method that closes the information gap:

| Situation | Method |
|---|---|
| 对方正在现场、会议中或可以即时回答 | 双向钢人访谈 |
| 对方掌握资料但暂时不能开会 | 信息缺口问卷 |
| 用户自己已经知道缺什么，但不知道怎么问全面 | 信息缺口问卷 |
| 业务主动提出功能，需求价值和边界不清 | 双向钢人访谈 |
| 事实可由 Agent 查到 | Agent 先查，不问人 |
| 只是用户已确认的执行任务 | 不启动本 Skill |

## Guardrails for the PM

- 默认只追问会影响范围、优先级、方案或验收的关键问题。
- 一轮最多提出 1–3 个真正需要用户决定的问题；不要把用户变成填问卷的人。
- 用户已经明确的判断不再强行构造反方。
- “钢人”不是为了反驳用户，而是先准确重述对方观点，再补齐反方风险和改变决定的条件。
- 不替用户决定业务取舍；Agent 负责结构化，用户或业务负责人负责拍板。
- 能查到的事实不转嫁给业务方，不让用户重复做检索。
- 复杂问题先给当前已知结论，再列未决问题；不要用提问掩盖已知事实。

## Mode A: 双向钢人访谈

### Step 1: 重述功能答案

先把对方的说法从“我要某功能”重述成可验证的问题：

> “我先确认一下：你现在提出的是『XX 功能』，但我们真正要解决的是哪一个业务问题？”

记录三类信息，不急着记录功能方案：

- 当前怎么做；
- 哪一步最痛；
- 痛点对个人、部门、客户或公司造成什么影响。

Done when the current process, concrete pain point, and affected party are explicit.

### Step 2: 反方钢人

准确理解需求后，再测试不做的代价：

> “假设这期不做 XX，最坏会发生什么？”

继续追问：

- 是效率下降、收入损失、合规风险、客户流失，还是体验不佳？
- 影响发生频率如何？
- 能否用现有流程暂时绕过？
- 业务愿意承担这个后果多久？

不要把“说不出金额”直接等同于伪需求；有些风险难以量化，但必须明确证据和严重程度。

Done when the consequence of not doing the request and its evidence are stated.

### Step 3: 找决策变量

询问：

> “这件事里，哪个因素真正会让你改变优先级或方案？”

常见变量包括：

- 客户投诉或流失；
- 领导要求；
- 交付期限；
- 法规或审计；
- 数据准确性；
- 开发成本；
- 业务覆盖范围；
- 与其他系统的依赖。

Done when the variable that could change the decision is named.

### Step 4: 压缩为最小动作

询问：

> “如果这一期只能做一个动作，哪个动作最能缓解核心痛点？”

再确认：

- 哪些内容明确放到后续；
- 不做这些内容的可接受后果；
- 最小动作如何验收；
- 谁拥有最终拍板权。

Done when the MVP boundary, deferred scope, acceptance signal, and decision owner are explicit.

### Interview Templates

#### 立项/首次需求收集

1. “你现在在线下或手工是怎么做的？”
2. “最麻烦的是哪一步？”
3. “这一步出问题会影响谁？”
4. “如果这期不做，最直接的后果是什么？”
5. “如果只能先解决一件事，你选哪一件？”

#### 需求确认

1. “这几个需求里，哪个不用会出问题？”
2. “B、C 延后到下一期，实际会造成什么影响？”
3. “请用一个真实业务例子说明每天怎么使用。”
4. “最终由谁确认范围和验收？”

#### 需求变更/扯皮

1. “不改这一点，当前版本还能不能用？”
2. “它是必须本期上线，还是下一期也可以？”
3. “新增范围会替换掉哪一项原计划？”
4. “如果本期按原计划上线，谁确认可以接受这个边界？”

## Mode B: 信息缺口问卷

Use this mode when the user cannot answer alone because the recipient holds the missing context.

### Step 1: Grill the Send, Not the Subject

Ask only two groups of questions:

1. **发送给谁？**
   - 对方角色；
   - 对方掌握的领域；
   - 对方与用户的关系；
   - 适合正式、简洁还是讨论式语气。

2. **需要拿回什么？**
   - 用户需要确认哪些事实；
   - 需要对方做哪些决策；
   - 得到答案后，用户要据此采取什么行动。

Do not make the user answer questions whose answers can be found by Agent tools.

Done when the recipient and a concrete list of required facts or decisions are known.

### Step 2: Write the Smallest Useful Questionnaire

Default to 5–10 high-value questions. Order them by importance because async recipients may only complete the first part.

Rules:

- One question contains one core fact or decision;
- Add a short “为什么重要” only when the question could be misunderstood;
- Provide an answer stub under every question;
- Allow “不清楚/待确认” as a valid answer;
- Group questions by theme only when there are more than a handful;
- Include enough context for someone outside the user's head, but not a long背景说明;
- End with an open catch-all question.

### Questionnaire Template

```markdown
# <问卷标题>

**目的：** <这份问卷要解决什么信息缺口，以及答案将支持什么决定>

**发起人：** <用户>
**填写人：** <收件人角色>
**答案用途：** <会写入哪里，或将支持什么行动>

## 背景

<一段足够让收件人理解问题的背景，不超过一页>

## 填写方式

请按问题顺序回答。部分回答、“不清楚”或“需要进一步确认”都很有价值，请直接标注，不必跳过。

## <主题>

### <问题一>

_为什么重要：<仅在必要时填写>_

> 

### <问题二>

> 

## 其他补充

还有哪些我们没有问到、但会影响判断或执行的信息？

> 
```

### Output Behavior

- 默认先在当前对话中输出问卷草稿，不自动写文件。
- 只有用户明确说“保存”“写成 Markdown”“发给我文件”时，才写入文件。
- 用户指定位置时按指定位置写；未指定位置时使用当前工作目录下的 `to-questionnaire-<slug>.md`。
- 写入后验证文件存在，并确认每个信息缺口都有对应问题。
- 不把问卷混入项目 `context/`、PRD 或笔记库，除非用户明确指定。

## Output: Convert Answers into Decisions

问卷或访谈收回答案后，不要只堆原文。整理成四层：

1. **已确认事实**：对方明确说了什么；
2. **待确认事实**：仍缺谁、缺什么；
3. **决策结论**：范围、优先级、方案、验收或责任人；
4. **后续动作**：谁在何时做什么。

业务规则或术语稳定后，才建议回写项目的权威文档。不要擅自创建第二套事实源。

## Forge Project Adaptation

For Forge projects, follow the existing authority hierarchy:

```text
context/ > templates/ > prd-docs/
```

- 业务事实、术语、边界写入或修正 `context/`；
- 文档结构遵循 `templates/`；
- `prd-docs/` 是产物，不是规则源；
- 技术架构决策只有在确实难以逆转、存在真实权衡且未来读者会困惑时，才记录到 `docs/adr/`；
- 不默认创建根目录 `CONTEXT.md`；
- 不把访谈草稿或问卷直接当作已确认业务规则。

## Common Pitfalls

1. **把功能要求当成需求结论**：先问现状、痛点和不做后果，再讨论方案。
2. **过度钢人化**：用户已经拍板后仍强行找反方，导致对话拖长；只处理会改变决策的反例。
3. **让用户查 Agent 能查到的事实**：先用文件、代码、网页或系统工具核实。
4. **问卷问太多**：先保留 5–10 个最影响决策的问题。
5. **一个问题塞多个决定**：拆开，确保每题只有一个答案目标。
6. **把问卷当 PRD**：问卷是信息收集工具，不是最终业务规则。
7. **自动写文件污染项目**：默认先给草稿，明确要求后再落盘。
8. **沉淀到错误位置**：Forge 中不要绕过 `context/` 创建第二套事实源。
9. **没有收口**：答案回收后必须产出事实、决策、待确认项和行动清单。

## Verification Checklist

- [ ] 已判断这是访谈、问卷、普通执行还是 Agent 可直接查证的任务
- [ ] 访谈已明确现状、痛点、影响、不做后果、决策变量和最小动作
- [ ] 问卷已明确收件人和信息缺口
- [ ] 问卷优先覆盖最重要的 5–10 个问题
- [ ] 每个问题只有一个核心答案目标
- [ ] 没有把用户已拍板内容重新拉入无休止论证
- [ ] 默认没有擅自写入文件
- [ ] 回收答案后已区分事实、决策、待确认项和后续动作
- [ ] Forge 项目遵守 `context/ > templates/ > prd-docs/`
