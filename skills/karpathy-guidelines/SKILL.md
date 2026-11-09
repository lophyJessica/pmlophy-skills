---
name: karpathy-guidelines
description: "Reduce common LLM coding mistakes — surface assumptions before coding, keep code minimal, make surgical edits, define verifiable success criteria. Load when writing/reviewing/refactoring code, incl. cleaning up AI-generated frontend or PRD-driven scaffolds. Derived from Andrej Karpathy's LLM-coding-pitfall observations (MIT)."
version: 1.0.0
author: Andrej Karpathy (via multica-ai/andrej-karpathy-skills, MIT); adapted by Jessica
license: MIT
metadata:
  tags: [coding, code-review, llm-behavior, quality, karpathy]
---

# Karpathy Guidelines

Four behavioral guidelines that reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls. MIT-licensed, from `multica-ai/andrej-karpathy-skills`.

**Tradeoff:** bias toward caution over speed. For trivial tasks (typo fixes, obvious one-liners), use judgment — don't over-apply.

## Trigger / When to load
- Writing, reviewing, or refactoring code (any language)
- Generating or cleaning up AI-produced code — e.g. the 强盛科技 `front-prototype/` pages, PRD-driven scaffolds
- Before any AI (Antigravity / Cursor / Claude Code, or me) makes multi-file or non-trivial code changes

## 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility"/"configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Test: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Remove imports/vars/functions that YOUR changes made unused; don't remove pre-existing dead code unless asked.
- Test: every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"
- For multi-step tasks, state a brief plan of `Step → verify: check` lines.
- Strong success criteria let the model loop independently; weak criteria ("make it work") force constant clarification.

## Reference
- `references/examples.md` — real before/after (❌ wrong vs ✅ right) code examples for each of the four principles.

## Deploying these rules to an AI IDE
Same four principles, one file per tool, placed at the **project root**:
- **AGENTS.md** — universal; Claude Code, Codex, Cursor, and Antigravity all read it. Simplest cross-tool option (append the principles here).
- **Antigravity / Windsurf** — `.agents/rules/<name>.md`; frontmatter `alwaysApply: true` (some versions use `trigger: always_on`). Antigravity (反重力) is Lophy's primary IDE, so this is the usual target.
- **Cursor** — `.cursor/rules/<name>.mdc`; frontmatter `description:` + `alwaysApply: true`.
- **Claude Code** — root `CLAUDE.md`, or install via the plugin marketplace.

Pitfall: this repo ships Cursor + CLAUDE.md versions but NOT an Antigravity one — you must author the `.agents/rules/` file yourself. Lophy prefers it delivered as **pasted text in chat**, not as an `.md` attachment. Source repo: `multica-ai/andrej-karpathy-skills` (MIT).

## Lineage note
This is the **root** source that PM 维他命老师's "AI 跑偏六种类型" builds on: Karpathy = 工程根准则, 维他命 = PM 化落地。See `/root/notes/vitamin-course/00-脉络与提炼.md`.
