# Agent / IDE Selection and Harness Fit

## Validated ranking for the user's current workflow

The user's practical ranking after real Forge tasks is:

- Agent execution: Codex > Workbuddy > Antigravity.
- AI IDE: Cursor is the strongest, with no second place currently.

This ranking is task-dependent, not a universal model benchmark. Select by the full harness loop: baseline inspection, bounded edits, preservation checks, build, packaging, upload, report, and human-gated deployment.

## Decision table

| Task shape | Preferred tool | Reason |
|---|---|---|
| Existing-project batch UI migration with clear samples and constraints | Workbuddy | Fast ordinary model plus a strong execution harness; validated on ERP 9 business modules and 4 master-data modules |
| High-quality diagnosis, read-only inspection, structured engineering implementation | Codex | More deliberate and thorough; slower but useful when uncertainty or architectural risk is high |
| Visual refinement, screenshot-driven UI fixes, cross-audit | Cursor | Best visual/interaction judgment and controlled IDE workflow |
| Rapid prototype, ProLayout skeleton, narrowly bounded mechanical styling | Antigravity | Useful when scope is small and the task does not threaten existing integrations |

## Harness-first evaluation

Do not rank tools only by model name or single-turn answer quality. For production work, verify whether the agent:

1. reads the current project and existing samples before editing;
2. preserves pre-existing uncommitted changes and integration anchors;
3. avoids inventing fields, mock data, routes, or business rules;
4. completes build and real validation;
5. packages a unique root-level ZIP;
6. uploads through the project's delivery pipeline;
7. writes a self-check report;
8. distinguishes upload from deployment;
9. leaves deployment behind a human approval gate.

A fast ordinary model that completes this loop is preferable to a slower stronger model that requires repeated steering or leaves handoff work to the user.

## Practical rule

For a clear, bounded task on an existing project, prefer the fastest tool that has already demonstrated a complete delivery loop. Reserve slower, stronger reasoning for uncertainty, diagnosis, architecture, or high-risk changes. Use Cursor for the final visual pass even when another agent performs the bulk migration.
