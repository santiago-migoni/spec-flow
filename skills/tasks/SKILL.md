---
name: tasks
description: "Break a plan into an ordered, checkable task list with exact file paths — the direct input for the implement phase. Use this after plan.md is approved and before writing any code."
---

# Spec-Flow: Tasks

Decompose the implementation plan into atomic, ordered, checkable tasks. This is the last artifact before code is written.

<HARD-GATE>
Before proceeding:
1. `.specs/NNN-feature-name/spec.md` must exist
2. `.specs/NNN-feature-name/plan.md` must exist — if not, stop and invoke `spec-flow:plan`
</HARD-GATE>

## When to Run This Phase

- After `plan.md` is written and approved
- Before any code is written for this feature

## Process

1. **Read `spec.md` and `plan.md`** for the current feature
2. **Identify task groups** — group by user story so each story can be independently verified
3. **Order tasks by dependency** — tasks that others depend on come first
4. **Mark parallel tasks** — use `[P]` for tasks that can run concurrently (they touch different files)
5. **Include exact file paths** in every task description
6. **Write `.specs/NNN-feature-name/tasks.md`** using `assets/tasks-template.md` as the output format
7. **Summarize and confirm** — report an executive summary (150 words max, never the full document — task count per phase/user story is enough), then ask for approval or revisions
8. **On revision request** — edit `tasks.md` directly, then repeat step 7 with a summary of what changed

## Task Format

Each task line follows this pattern:

```
- [ ] T001 [US1] Description with exact/file/path.ts
- [ ] T002 [P][US1] Another task touching different/file.ts (parallel with T001)
- [ ] T003 [US2] Depends on T001 — description with path
```

- `[P]` = can run in parallel with other `[P]` tasks in the same group
- `[US1]`, `[US2]` etc. = which user story this task delivers
- Every task that creates or modifies a file must include the full path

## Sizing Guide

A well-sized task takes 5–15 minutes. If a task description needs more than one sentence, split it. If it needs fewer than 5 minutes, consider merging it with a related task.

## Quality Check Before Writing

- [ ] Every task is atomic — can be completed in one focused step
- [ ] Every task that touches a file includes the full path
- [ ] Tasks are ordered so no task depends on a later task
- [ ] Every user story in `spec.md` is covered by at least one task
- [ ] The VERIFY tasks at the end map to acceptance scenarios in `spec.md`

## After Writing

Tell the user: "Tasks written to `.specs/NNN-feature-name/tasks.md`. Run `spec-flow:analyze` first for a consistency check (recommended, not required), or `spec-flow:implement` directly to begin execution."
