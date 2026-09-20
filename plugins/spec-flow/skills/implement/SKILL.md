---
name: implement
description: "Implement one phase of approved tasks.md per invocation: read its tasks, code, validate, and commit that phase. Use this when tasks.md exists and it's time to write code."
---

# Spec-Flow: Implement

Execute the task list one phase per invocation. Within that phase, complete tasks in order and close the phase with validation and a commit before moving on in a later invocation.

<HARD-GATE>
Before proceeding:
1. `.specs/NNN-feature-name/tasks.md` must exist with document-control `Status: Approved` — otherwise stop and invoke `$tasks` or request approval
2. `.specs/NNN-feature-name/spec.md` must exist with document-control `Status: Approved` or `Converged` — otherwise stop and invoke `$specify` or request approval
3. `.specs/NNN-feature-name/plan.md` must exist with document-control `Status: Approved` — otherwise stop and invoke `$plan` or request approval
</HARD-GATE>

## When to Run This Phase

- After `tasks.md` is written and approved
- This is the only phase where code is written

## Code Philosophy

Write the minimal code that satisfies the acceptance scenario — nothing more. If a task can be done in 5 lines instead of 20, do it in 5. Do not add abstractions, helpers, or "nice to have" structure unless a task explicitly requires it.

## Process

1. **Read `tasks.md`, `spec.md`, and `plan.md`** — identify the first phase with unchecked tasks and read all tasks in that phase. If no tasks remain, run the bundled `check-complete.sh` and report that implementation is ready for `$converge`; do not create an empty commit.
2. **Inspect the worktree and recent commits** — confirm that any changes already present in the phase's files and `tasks.md` are understood. Preserve unrelated edits. If the phase's changes cannot be separated safely from pre-existing work, stop and explain the overlap.
3. **Execute only that phase's tasks in order**, one at a time:
   - Announce which task you are starting: "Starting T002 [US1] — ..."
   - Complete the task
   - Mark it done in `tasks.md`: change `- [ ]` to `- [x]`
   - Confirm completion before moving to the next task
4. **For `[P]` tasks** — execute in sequence within the same session (no subagents); the `[P]` marker is informational, indicating they touch independent files.
5. **Validate the phase** — run the tests or checks relevant to its tasks and observe any acceptance scenarios the phase makes executable. If this is the final phase, complete the full Verification Step below before committing. If a check fails, fix it within the same phase and rerun it. If validation remains blocked, report the failure and leave the phase uncommitted; resume this phase next time.
6. **Commit the validated phase** — stage only the phase's changed files and `tasks.md`, using explicit paths. Inspect the staged diff and status to confirm it contains no unrelated work or secrets, then create one Conventional Commit describing the phase. If committing is unavailable or unsafe, stop before the next phase and report why.
7. **Stop after this phase** — report its completed task IDs, validation evidence, and commit SHA. On the next `$implement` invocation, resume with the first phase that still has unchecked tasks. Never automatically start the next phase in the same invocation.

## Verification Step

When the phase just completed is the final phase, do the full verification below before its commit:

1. **Read every acceptance scenario** in `spec.md`
2. **Confirm each one is satisfied** by executing the flow affected by the change and observing the actual behavior — not by tracing to `file:line`. State it explicitly: "US1 scenario 1: Given X, When Y, Then Z → ran [command/flow] → observed [actual behavior]"
3. **If a scenario is not satisfied** — add a task to the current phase in `tasks.md`, fix it, then re-run the flow and re-verify before committing
4. **If a change has no executable surface** (prompt-only / docs — e.g. editing a spec-flow `SKILL.md` itself) — degrade to reviewing the artifact's expected behavior instead, and state explicitly why nothing was run. This is not a fallback of last resort — it's the correct path for changes with no runtime to exercise. A change with partial executable surface runs what can be run and degrades only the rest.
5. **Check against constitution** — confirm no principle in `.specs/constitution.md` was violated
6. **Run completion check** — resolve the plugin package root from this skill's installed `SKILL.md` path in Codex's skill inventory, then run its `scripts/check-complete.sh .specs/NNN-feature-name/tasks.md`

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
| "I'll run every remaining phase now" | Finish and commit the current phase, then stop. The next invocation starts the next phase. |
| "I'll verify only after every phase is done" | Validate each phase before its commit; run all acceptance scenarios after the final phase. |

## After Verification

After an intermediate phase, tell the user which phase was committed and which phase is next. After the final phase, tell the user: "All tasks complete. Feature `NNN-feature-name` is done. Acceptance scenarios verified. Ready to run `$converge`."
