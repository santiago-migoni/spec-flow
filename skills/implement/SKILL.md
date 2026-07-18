---
name: implement
description: "Execute tasks from tasks.md one by one, marking each complete, then verify all acceptance scenarios from spec.md pass. Use this when tasks.md exists and it's time to write code."
model: sonnet
effort: medium
---

# Spec-Flow: Implement

Execute the task list systematically. No task is skipped, no task is batched with another, each is checked off before the next begins.

<HARD-GATE>
Before proceeding:
1. `.specs/NNN-feature-name/tasks.md` must exist — if not, stop and invoke `spec-flow:tasks`
2. `.specs/NNN-feature-name/spec.md` must exist (needed for final verification)
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
6. **After all tasks are checked** — run `scripts/check-complete.sh .specs/NNN-feature-name/tasks.md` to confirm, then proceed to the Verification Step

## Verification Step

After all implementation tasks are done:

1. **Read every acceptance scenario** in `spec.md`
2. **Confirm each one is satisfied** by executing the flow affected by the change and observing the actual behavior — not by tracing to `file:line`. State it explicitly: "US1 scenario 1: Given X, When Y, Then Z → ran [command/flow] → observed [actual behavior]"
3. **If a scenario is not satisfied** — add a new task to `tasks.md` to fix it, execute it, then re-run the flow and re-verify
4. **If a change has no executable surface** (prompt-only / docs — e.g. editing a spec-flow `SKILL.md` itself) — degrade to reviewing the artifact's expected behavior instead, and state explicitly why nothing was run. This is not a fallback of last resort — it's the correct path for changes with no runtime to exercise. A change with partial executable surface runs what can be run and degrades only the rest.
5. **Check against constitution** — confirm no principle in `.specs/constitution.md` was violated

Executing a flow must never run a destructive or irreversible action (data writes, deletions, external calls with side effects) without the explicit per-action confirmation the constitution already requires elsewhere — observe behavior, don't cause damage to observe it.

## What Counts as Done

A feature is done when:
- All tasks in `tasks.md` are `[x]`
- All acceptance scenarios in `spec.md` are executed and confirmed by observed behavior (or reviewed, for changes with no executable surface)
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
