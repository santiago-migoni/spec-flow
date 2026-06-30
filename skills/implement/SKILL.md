---
name: implement
description: "Execute tasks from tasks.md one by one, marking each complete, then verify all acceptance scenarios from spec.md pass. Use this when tasks.md exists and it's time to write code."
---

# Spec-Flow: Implement

Execute the task list systematically. No task is skipped, no task is batched with another, each is checked off before the next begins.

<HARD-GATE>
Before proceeding:
1. `specs/NNN-feature-name/tasks.md` must exist — if not, stop and invoke `spec-flow:tasks`
2. `specs/NNN-feature-name/spec.md` must exist (needed for final verification)
</HARD-GATE>

## When to Run This Phase

- After `tasks.md` is written and approved
- This is the only phase where code is written

## Code Philosophy

Write the minimal code that satisfies the acceptance scenario — nothing more. If a task can be done in 5 lines instead of 20, do it in 5. Do not add abstractions, helpers, or "nice to have" structure unless a task explicitly requires it.

## Process

1. **Read `tasks.md`** — identify the first unchecked task
2. **Read `spec.md`** — keep acceptance scenarios in mind throughout
3. **Execute tasks in order**, one at a time:
   - Announce which task you are starting: "Starting T002 [US1] — ..."
   - Complete the task
   - Mark it done in `tasks.md`: change `- [ ]` to `- [x]`
   - Confirm completion before moving to the next task
4. **For `[P]` tasks** — execute in sequence within the same session (no subagents); the `[P]` marker is informational, indicating they touch independent files
5. **On blockers** — if a task cannot be completed as written (missing info, conflicting code), stop and surface the blocker to the user before proceeding. Do not guess or work around it silently.
6. **After all tasks are checked** — run `scripts/check-complete.sh specs/NNN-feature-name/tasks.md` to confirm, then proceed to the Verification Step

## Verification Step

After all implementation tasks are done:

1. **Read every acceptance scenario** in `spec.md`
2. **Confirm each one is satisfied** by the code written — trace it explicitly: "US1 scenario 1: Given X, When Y, Then Z → satisfied by [file:line]"
3. **If a scenario is not satisfied** — add a new task to `tasks.md` to fix it, execute it, then re-verify
4. **Check against constitution** — confirm no principle in `specs/constitution.md` was violated

## What Counts as Done

A feature is done when:
- All tasks in `tasks.md` are `[x]`
- All acceptance scenarios in `spec.md` are traced and confirmed
- No `[NEEDS CLARIFICATION]` markers remain anywhere in `spec.md` or `plan.md`
- The code compiles / lints / passes existing tests

## Anti-Patterns

| Thought | Reality |
|---|---|
| "I'll fix T003 while doing T002, it's related" | Complete T002, mark it done, then start T003. |
| "The task says X but Y is clearly better" | Update `tasks.md` with the revised approach and get confirmation first. Don't silently deviate. |
| "I'll add a helper utility while I'm here" | Ponytail: if the task doesn't require it, don't write it. |
| "I'll verify at the end of the whole session" | Verify immediately after all tasks are checked. Context is freshest now. |

## After Verification

Tell the user: "All tasks complete. Feature `NNN-feature-name` is done. Acceptance scenarios verified. Ready to run `spec-flow:converge`."
