# Tasks: Phase Approval Gate

| Name                | Code      | Version | Date       | Status   |
| -------------------- | --------- | ------- | ---------- | -------- |
| phase-approval-gate  | TASKS-003 | R01     | 2026-07-17 | Approved |

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
- [x] T008 [US1] Found via real `claude --debug` testing (not anticipated in `plan.md`): `hooks/check-phase-approval.sh`'s JSON output was missing the required `hookEventName` field inside `hookSpecificOutput`, causing Claude Code to discard the output as invalid and allow every call regardless of the computed decision — the `deny` path was silently a no-op. Fixed by adding `"hookEventName": "PreToolUse"` to both JSON emissions (the `allow()` function and the `deny` `printf`). Re-verified against a real `Status: Draft` artifact on the `003-phase-approval-gate` branch: correct `deny` + `systemMessage`, and correct `allow` once restored to `Approved`.
- [x] T009 [US1] Found by the user asking whether the hook protects anything on `main`: it didn't — a branch with no `.specs/<branch>/` (like `main`) fell into the same fail-open path as a grandfathered old-format artifact, silently allowing every call. Per `spec.md` R02's Clarifications, narrowed fail-open to *only* the grandfathered case (existing artifact, no `Status` column); a missing branch or a missing artifact file now `deny` with a specific `systemMessage` each. Rewrote `hooks/check-phase-approval.sh` with a `deny()` helper and the three-way message split documented in `plan.md`'s API/Interface Contracts. Re-verified all 6 paths standalone (non-Skill tool, unrelated skill, `specify`/`plan` allow, `Status: Draft` deny, and the new no-branch deny by checking out `main` and back).

## Verification

- [x] VERIFY All acceptance scenarios in spec.md pass — confirmed via real `claude --debug` testing (a gated call was denied when `Status` was `Draft`, allowed once `Approved`) plus standalone re-verification of the new no-branch/no-artifact `deny` paths (T009) after the `claude --debug` round, since those weren't part of the original debug session. `spec-flow:clarify`/`spec-flow:analyze` calls fall through the skill filter untouched. US2's scenarios remain verified via T007 (prose-level, not hook-enforced).
- [x] VERIFY All Non-Functional Requirements in spec.md are met, or the section is "N/A" — no network call in the hook script, `systemMessage` always present on deny, the check completes with no noticeable delay.
- [x] VERIFY No constitution MUST principle relevant to this feature is violated — Dependency Policy (`jq` deliberately not added), Code Principles' narrow R02/R03 hooks exception scope respected.
- [x] VERIFY No files were created that are not listed in plan.md's file structure — only `hooks/hooks.json` and `hooks/check-phase-approval.sh`.
- [x] VERIFY No new dependencies were added beyond those listed in plan.md.
