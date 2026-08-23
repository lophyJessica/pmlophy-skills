---
name: pm-prototype-decision
description: Build a disposable prototype to answer one product question about UI, workflow, state, or information architecture before changing production code.
version: 1.0.0
author: Lophy / Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [prototype, ui, workflow, state-machine, product-decision]
    related_skills: [pm-to-spec, pm-discovery-dialogue]
---

# PM Prototype Decision

## Overview

Use a throwaway prototype as a decision instrument, not as an accidental production implementation. The prototype must answer one named product question quickly, expose the relevant state or interaction, and leave the validated decision ready for the real implementation.

## When to Use

Use when:

- it is unclear what a page or workflow should look like;
- a state machine or business flow is hard to reason about on paper;
- multiple UI directions need comparison;
- a non-developer needs something concrete to react to;
- implementing directly would risk expensive rework.

Do not use when the design is already confirmed or when the task is a mechanical change to an existing page.

## Choose the Prototype Shape

- **UI question** — produce one runnable page with several clearly different variants, switchable without changing production routes.
- **Workflow/state question** — produce one runnable page with free-play actions and a guided walkthrough for important edge cases.
- **Information architecture question** — produce a small clickable skeleton that tests navigation and hierarchy, not visual polish.

If the question is ambiguous, state the assumption and choose the smallest artifact that can disambiguate it.

## Rules

1. Write the question at the top of the prototype.
2. Keep it disposable and clearly marked `PROTOTYPE`.
3. Locate it near the relevant work but outside production paths, or in a dedicated scratch area.
4. Make it runnable with one obvious command or by opening one HTML file.
5. Keep state in memory by default; do not connect real databases or production APIs.
6. Show the full relevant state after actions or variant changes.
7. Compare options honestly; do not silently make one option look better.
8. Skip production polish, broad error handling, and abstractions.
9. For users with visual impairment, provide a structured text description of each variant and state, not screenshots alone.

## Decision Loop

1. Name the question.
2. Build the smallest runnable artifact.
3. Let the user operate it or review structured output.
4. Record the verdict:
   - selected direction;
   - rejected directions and why;
   - unresolved questions;
   - production acceptance criteria.
5. Convert the verdict with `pm-to-spec` before changing real code.
6. Delete the prototype or keep it only where the project explicitly treats it as a reference artifact.

## Verification Checklist

- [ ] The prototype answers one explicit question.
- [ ] It runs without production credentials or data.
- [ ] Relevant states and transitions are visible.
- [ ] The user can compare or exercise the alternatives.
- [ ] The verdict and rejection reasons are recorded.
- [ ] No prototype-only code was mistaken for production code.
