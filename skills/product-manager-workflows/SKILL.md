---
name: product-manager-workflows
description: Product management workflows for software PMs. Use when Codex needs to turn ideas, customer problems, stakeholder requests, meeting notes, research, metrics, screenshots, or backlog items into PM deliverables such as PRDs, user stories, acceptance criteria, MVP scope, prioritization, release notes, experiment plans, competitor analysis, roadmap options, design review feedback, or engineering handoff specs.
---

# Product Manager Workflows

## Operating Principles

Start by identifying the artifact the user needs and the decision it should support. If the request is vague, infer a sensible default and state assumptions briefly instead of blocking.

Favor concrete product thinking:
- Define the user, problem, goal, constraints, and success metric before proposing features.
- Separate facts, assumptions, open questions, and recommendations.
- Make tradeoffs explicit: scope, timeline, risk, effort, dependencies, and user impact.
- Translate product intent into engineering-ready details when handoff is requested.
- Keep artifacts concise enough for a working team to read and act on.

For missing context, ask at most three high-value questions only when the output would otherwise be misleading. Otherwise, proceed with assumptions and mark them.

## Workflow Router

Use the smallest workflow that matches the request:

- PRD, feature spec, product requirements, or "write a requirements doc": use `references/prd-template.md`.
- User stories, acceptance criteria, Jira tickets, Linear issues, QA checklist, or engineering handoff: use `references/story-acceptance-template.md`.
- Competitor analysis, market scan, benchmark, positioning, or strategy memo: use `references/research-analysis-template.md`.
- Prioritization, roadmap, MVP, or scope tradeoff: produce options with impact, effort, confidence, risk, and recommendation.
- Meeting notes or messy input: extract decisions, requirements, risks, owners, open questions, and next actions.
- Design review or prototype critique: assess user goal fit, information hierarchy, interaction clarity, edge states, accessibility, and launch risk.

## Default PM Flow

1. Restate the product objective in one sentence.
2. Identify target users and top user jobs.
3. Convert the problem into measurable outcomes.
4. Propose the smallest useful scope first, then optional expansions.
5. List non-goals to prevent scope creep.
6. Define success metrics, guardrail metrics, and instrumentation needs.
7. Produce deliverables in the format the user requested.
8. End with open questions, risks, and recommended next steps when useful.

## Artifact Guidance

For PRDs, emphasize problem framing, success metrics, user scenarios, requirements, non-goals, dependencies, risks, rollout, analytics, and acceptance criteria. Do not bury key decisions in prose.

For tickets and user stories, include:
- User story
- Context
- Functional requirements
- Acceptance criteria in Given/When/Then where useful
- Edge cases
- Analytics or logging
- Dependencies
- Test notes

For prioritization, use a lightweight scoring table when the user gives multiple ideas. Prefer transparent scoring over false precision.

For research and competitor work, distinguish verified facts from inference. If current market information is needed, browse or ask for permission according to the active environment. Cite sources when using external information.

For stakeholder-facing writing, use crisp business language. For engineering-facing writing, use unambiguous behavior, states, inputs, outputs, errors, and data needs.

## Output Style

Match the user's requested language. If not specified, use the user's language.

Use tables for comparison, prioritization, acceptance criteria matrices, and roadmap options. Use bullets for requirements and risks. Use short prose for reasoning and recommendations.

Avoid overproducing long documents when the user asks for a quick draft. Offer a compact version first unless the user asks for a full spec.

## References

Read only the relevant reference:
- `references/prd-template.md` for PRDs and feature specs.
- `references/story-acceptance-template.md` for stories, acceptance criteria, tickets, and QA.
- `references/research-analysis-template.md` for competitor, market, user research, and analytics analysis.
