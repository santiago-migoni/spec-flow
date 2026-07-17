# Tasks: Phase Approval Gate

| Name                | Code      | Version | Date       | Status   |
| -------------------- | --------- | ------- | ---------- | -------- |
| phase-approval-gate  | TASKS-003 | R00     | 2026-07-17 | Approved |

## Phase 1: Setup

- [x] T001 [setup] Create `hooks/` directory in the repo root per `plan.md`'s file structure.

## Phase 2: US1 — Block invoking the next phase before approval (P1)

- [x] T002 [US1] Write `hooks/check-phase-approval.sh`: extract `tool_name` and the invoked skill's name from stdin JSON via grep/sed (no `jq`, per `plan.md`'s Dependency Policy decision); allow immediately (no-op) if the skill isn't one of `spec-flow:specify`/`plan`/`tasks`/`implement`.
- [x] T003 [US1] `hooks/check-phase-approval.sh` — depends on T002 — resolve the prior artifact's path from `git branch --show-current`, per `plan.md`'s gated-skill → prior-artifact mapping table.
- [x] T004 [US1] `hooks/check-phase-approval.sh` — depends on T003 — extract the `Status` cell from the resolved artifact's document-control table data row via grep/sed.
- [x] T005 [US1] `hooks/check-phase-approval.sh` — depends on T004 — emit `{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "<reason>"}` when `Status` is exactly `Draft`, and `{"hookSpecificOutput": {"permissionDecision": "allow"}}` for every other case (missing file, missing column, any other value, parse error).
- [x] T006 [P][US1] Write `hooks/hooks.json`: register the `PreToolUse` hook, matcher `"Skill"`, command pointing to `${CLAUDE_PLUGIN_ROOT}/hooks/check-phase-approval.sh` (independent of T002-T005, different file).

## Phase 3: US2 — Record approval as part of the existing confirm step (P1)

- [x] T007 [US2] Confirm `skills/constitution/SKILL.md`, `skills/specify/SKILL.md`, `skills/plan/SKILL.md`, and `skills/tasks/SKILL.md` each already cover all three of US2's acceptance scenarios: (a) an "On approval — set `Status` to `Approved`" step, (b) the pre-approval revise loop leaves `Status` at `Draft`, and (c) any edit requested *after* approval resets `Status` back to `Draft` (with the two-case refinement for already-shown/approved edits). All three confirmed present — verified 2026-07-17, no new edits needed.

## Verification

- [ ] VERIFY All acceptance scenarios in spec.md pass — via `claude --debug` (after restarting the session so the new hook loads): a gated call is denied when the prior artifact's `Status` is `Draft`, and allowed when `Approved`/`Converged`/missing column; `spec-flow:clarify`/`spec-flow:analyze` calls are never blocked.
- [x] VERIFY All Non-Functional Requirements in spec.md are met, or the section is "N/A" — no network call in the hook script, `systemMessage` always present on deny, the check completes with no noticeable delay.
- [x] VERIFY No constitution MUST principle relevant to this feature is violated — Dependency Policy (`jq` deliberately not added), Code Principles' narrow R02/R03 hooks exception scope respected.
- [x] VERIFY No files were created that are not listed in plan.md's file structure — only `hooks/hooks.json` and `hooks/check-phase-approval.sh`.
- [x] VERIFY No new dependencies were added beyond those listed in plan.md.
