---
name: pm-handoff
description: Compact the current task into a portable handoff so a new session, model, agent, or collaborator can continue without replaying the whole conversation.
version: 1.0.0
author: Lophy / Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [handoff, session, context, agents, token-efficiency]
    related_skills: [pm-research, pm-to-spec, pm-discovery-dialogue]
---

# PM Handoff

## Overview

Create a compact, portable handoff when the current session is getting long, work is moving to another agent, or a collaborator needs to continue from a known state. The handoff is a pointer map, not a transcript: reference existing files, reports, commits, URLs, and artifacts instead of duplicating their contents.

## When to Use

Use when:

- a long session should be closed before context cost grows;
- work moves from Hermes to Codex, Workbuddy, Cursor, or another session;
- a task is paused between research, implementation, testing, and deployment;
- a collaborator needs the current status and exact next action;
- the user asks for a session handoff or continuation brief.

Do not use when a task is already complete and no continuation is needed, or when a short direct reply is enough.

## Handoff Contents

Include only what the next actor needs:

1. **Mission** — the outcome being pursued.
2. **Current state** — confirmed facts, not guesses.
3. **Completed work** — concise bullets with paths, URLs, commit IDs, or report names.
4. **Open work** — unfinished items and their blockers.
5. **Next action** — one executable next step, including who acts and where.
6. **Constraints** — scope, red lines, user decisions, and things not to repeat.
7. **Suggested skills** — skills the next actor should load.
8. **Evidence map** — pointers to authoritative source files, reports, builds, or deployments.

## Rules

- Never replay the full conversation.
- Never turn an unverified agent claim into a confirmed fact.
- Distinguish “uploaded”, “deployed”, “HTTP 200”, “user verified”, and “committed/pushed”.
- Redact passwords, API keys, tokens, private personal data, and sensitive endpoints.
- Do not invent missing status. Write “unknown” or “needs verification”.
- Preserve the user's language, decisions, and scope boundaries.
- If a new session is the intended next step, say so explicitly; do not recommend `/new` when the current context is still required.

## Output Modes

### In conversation

Default: output the handoff inline in concise Markdown. Do not create a file unless the user asks.

### File handoff

When the user asks to save it, write to a temporary or user-specified location, not automatically into a project root. Use a descriptive name such as `handoff-<topic>-<date>.md`. Verify that the file exists and report its absolute path.

## Template

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

## Verification Checklist

- [ ] Mission is clear in one paragraph.
- [ ] Every completed claim has a pointer or is marked as user-confirmed.
- [ ] Open work and next owner are explicit.
- [ ] No sensitive values or duplicated long artifacts are included.
- [ ] The handoff is shorter than the context it replaces.
