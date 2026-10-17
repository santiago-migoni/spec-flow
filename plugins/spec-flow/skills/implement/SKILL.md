---
name: implement
description: "Implement the approved tasks of one release in order, running each step's verification and reporting the results."
---

# Spec-Flow: Implement

<HARD-GATE>
Require current registry approvals for the release's spec, plan, and tasks, and their strategic dependencies. Run `gate` with `{"phase":"implement","release":"vX.Y.Z"}`; it must report ready. If it does not, stop and report the missing or stale approval. Do not implement against legacy `.specs/NNN-feature-name` artifacts.
</HARD-GATE>

## Scope

Build the approved tasks in `.specs/release-vX.Y.Z/tasks.md`, in dependency order. Work directly in the project with normal tools. No delegation, profiles, leases, or controller-tracked task state are needed.

## Per task

1. Read the task, its acceptance criteria in `spec.md`, and its listed `files`. Only change those files; if a change must touch another file, stop and update `tasks.md` first, through `tasks`.
2. Work through the ordered `steps`. For each step, make the change and run its `verification` command (or perform its `inspection`) exactly as written.
3. A step is done only when its command exits 0 and its observed output matches `expected`. Do not change the verification to make it pass.
4. When every step of the task passes, check the task's `closure` statement and move to the next task.

## Blockers

If a verification fails and the fix is inside the task's files, fix it and rerun. If the fix needs a file outside the task, or a change to the behavior the spec describes, stop and return to the owning skill (`tasks`, `plan`, or `specify`). Report the failing command and its output.

## Report

After the last task, report: the tasks completed, the verification results (command and outcome), anything skipped or still failing, and the files changed. Do not claim a task is complete if any of its steps did not pass.

Commits and pushes are separate and need their own instruction from the user.
