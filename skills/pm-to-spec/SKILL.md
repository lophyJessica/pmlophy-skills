---
name: pm-to-spec
description: Turn an already-discussed product decision into an agent-ready implementation specification without reopening settled questions.
version: 1.0.0
author: Lophy / Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [product-spec, agent-instructions, scope, acceptance, handoff]
    related_skills: [pm-discovery-dialogue, pm-handoff, pm-research]
---

# PM to Spec

## Overview

Convert a conversation, confirmed research result, or approved product decision into a compact specification that Codex, Workbuddy, Cursor, or another execution agent can act on. This is synthesis, not another interview.

## When to Use

Use when:

- the user has already discussed and confirmed the goal;
- a researched decision needs to become executable work;
- a task must be handed to an external coding agent;
- a large request needs a clear scope, preservation layer, and acceptance gate.

Do not use when key product decisions remain unresolved; use `pm-discovery-dialogue` first. Do not use for a trivial one-line instruction.

## Process

1. **Read the source conversation and artifacts** — do not ask again what is already known.
2. **State the problem from the user's perspective.**
3. **Define the desired outcome and user-visible behavior.**
4. **Separate change layer from preservation layer.**
5. **List scope and explicit out-of-scope items.**
6. **Write constraints, red lines, dependencies, and data-model limits.**
7. **Define verification from external behavior first, then build/tests and delivery evidence.**
8. **Name the owner, machine, repository, branch, and deployment responsibility.**

If a contradiction is discovered, stop synthesis and surface the contradiction instead of silently choosing.

## Spec Template

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

## Agent Delivery Rules

For code tasks, begin the actual instruction with a direct execution sentence: modify the existing project, do not save the instruction as a document, and do not output only a plan.

Include:

- `git pull --ff-only` before edits;
- exact project path and target scope;
- existing work to preserve;
- build command;
- unique ZIP name and “解压即根” structure when packaging is required;
- complete copy-paste upload commands when the project pipeline requires them;
- explicit owner for upload and deployment;
- no claim of deployment without independent verification.

Do not make the agent infer the project path, reference page, data contract, or acceptance standard when those facts are available.

## Forge Adaptation

For Forge projects:

```text
context/ > templates/ > prd-docs/
```

- Use `context/` as the business source of truth;
- use `templates/` for document structure;
- treat `prd-docs/` as generated output;
- preserve Dexie schema, API contract, route structure, existing annotation anchors, and user changes unless explicitly in scope;
- separate local build, incoming upload, manual deployment, and user browser acceptance;
- never call HTTP 200 alone proof of a new deployment.

## Verification Checklist

- [ ] Spec synthesizes confirmed decisions without reopening them.
- [ ] Problem, outcome, scope, preservation layer, and out-of-scope are explicit.
- [ ] Every important claim has a source or is labeled as an assumption.
- [ ] Agent path, owner, branch, build, delivery, and acceptance are explicit.
- [ ] The specification is small enough for the chosen agent to execute reliably.
