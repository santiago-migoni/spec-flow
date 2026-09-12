# Tasks: Codex Plugin Migration

| Name                  | Code      | Version | Date       | Status |
| --------------------- | --------- | ------- | ---------- | ------ |
| codex-plugin-migration | TASKS-006 | R00     | 2026-09-12 | Approved |

## Phase 1: Setup

- [x] T001 [setup][US4] Amend `.specs/constitution.md` from R03 to R04, mark it Draft while preparing the Codex guidance, present it for approval, then mark it Approved and stop before T002 until the user approves it.

## Phase 2: User Story 1 — Installable Codex plugin (P1)

- [ ] T002 [US1] Create `plugins/spec-flow/plugin.json` with the portable Agent Plugins manifest, version `0.9.0`, and Codex hook path, and `.agents/plugins/marketplace.json` with the GitHub `git-subdir` source (`https://github.com/santiago-migoni/spec-flow.git`, `./plugins/spec-flow`, ref `main`) and marketplace policies.
- [ ] T003 [US1] Move `scripts/check-complete.sh` to `plugins/spec-flow/scripts/check-complete.sh` and keep its task-completion behavior unchanged.

## Phase 3: User Story 2 — Codex-native skill workflow (P1)

- [ ] T004 [P][US2] Move `skills/analyze/SKILL.md` and `skills/analyze/assets/report-template.md` to `plugins/spec-flow/skills/analyze/` and convert their metadata, activation language, and resource references for Codex.
- [ ] T005 [P][US2] Move `skills/backlog/SKILL.md` and `skills/backlog/assets/backlog-template.md` to `plugins/spec-flow/skills/backlog/` and convert their metadata and activation language for Codex.
- [ ] T006 [P][US2] Move `skills/clarify/SKILL.md` and `skills/clarify/assets/clarifications-template.md` to `plugins/spec-flow/skills/clarify/` and convert their metadata, activation language, and resource references for Codex.
- [ ] T007 [P][US2] Move `skills/constitution/SKILL.md` and `skills/constitution/assets/constitution-template.md` to `plugins/spec-flow/skills/constitution/` and update the skill's project-exploration guidance for Codex.
- [ ] T008 [P][US2] Move `skills/converge/SKILL.md` and `skills/converge/assets/convergence-report-template.md` to `plugins/spec-flow/skills/converge/` and convert the skill metadata and activation language for Codex.
- [ ] T009 [P][US2] Move `skills/finishing-branch/SKILL.md` to `plugins/spec-flow/skills/finishing-branch/SKILL.md` and update its Codex activation language, bundled helper path, and version-file examples.
- [ ] T010 [P][US2] Move `skills/implement/SKILL.md` to `plugins/spec-flow/skills/implement/SKILL.md`, preserve its hard gate, and resolve `check-complete.sh` from the bundled plugin path.
- [ ] T011 [P][US2] Move `skills/plan/SKILL.md` and `skills/plan/assets/plan-template.md` to `plugins/spec-flow/skills/plan/` and convert their metadata, activation language, and resource references for Codex.
- [ ] T012 [P][US2] Move `skills/specify/SKILL.md`, `skills/specify/assets/spec-template.md`, and `skills/specify/scripts/next-feature-number.sh` to `plugins/spec-flow/skills/specify/` and resolve the bundled helper from the skill path.
- [ ] T013 [P][US2] Move `skills/tasks/SKILL.md` and `skills/tasks/assets/tasks-template.md` to `plugins/spec-flow/skills/tasks/` and convert their metadata, activation language, and resource references for Codex.
- [ ] T014 [P][US2] Move `skills/using-spec-flow/SKILL.md` to `plugins/spec-flow/skills/using-spec-flow/SKILL.md` and update its phase tables and skill-invocation examples for Codex.

## Phase 4: User Story 3 — Approval gates in Codex (P1)

- [ ] T015 [US3] Move `hooks/hooks.json` to `plugins/spec-flow/hooks/hooks.json` and replace the Claude `Skill` matcher with Codex `PreToolUse` matchers for `apply_patch`, `Edit`, and `Write`.
- [ ] T016 [US3] Implement `plugins/spec-flow/hooks/check-phase-approval.py` with structured Codex event parsing and denial reasons, then delete `hooks/check-phase-approval.sh`.

## Phase 5: User Story 4 — Codex repository guidance (P2)

- [ ] T017 [US4] Rewrite `README.md` for Codex installation and usage while keeping its seven-phase and optional-skill tables aligned with `plugins/spec-flow/skills/using-spec-flow/SKILL.md`.
- [ ] T018 [P][US4] Rewrite `AGENTS.md` to match the package paths and add the migration entry under a new `## Unreleased` heading in `CHANGELOG.md` without bumping the plugin version.
- [ ] T019 [P][US4] Delete `CLAUDE.md`, `.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json` so no Claude package or maintainer instructions remain active.

## Phase 6: User Story 5 — Install from the repository marketplace (P2)

- [ ] T020 [US5] Add the exact `codex plugin marketplace add santiago-migoni/spec-flow --ref main` and `codex plugin add spec-flow@spec-flow-repo` steps to `README.md` and verify they resolve the GitHub marketplace name and package path without a local checkout.
- [ ] T021 [US5] In an isolated, reversible Codex configuration, add the marketplace from GitHub at ref `main`, install `spec-flow`, confirm the package and all 11 skills are listed, then remove the test marketplace and plugin. If the migrated commit is not yet available on GitHub `main`, record the remote end-to-end check as pending publication and do not substitute a local source.

## Verification

- [ ] VERIFY All acceptance scenarios in `.specs/006-codex-plugin-migration/spec.md` pass, including marketplace installation and discovery of all 11 skills.
- [ ] VERIFY All Non-Functional Requirements in `.specs/006-codex-plugin-migration/spec.md` are met, including the portable manifest, marketplace source resolution, Codex metadata, and documented hook limits.
- [ ] VERIFY No constitution MUST principle relevant to this feature is violated after the user approves `.specs/constitution.md` R04.
- [ ] VERIFY Every created or modified file is listed in `.specs/006-codex-plugin-migration/plan.md` and no plugin payload remains at the old root `skills/`, `hooks/`, or `scripts/` paths.
- [ ] VERIFY No dependencies were added beyond Python 3 standard-library JSON parsing and the existing Bash environment.
- [ ] VERIFY The approval hook allows unaffected writes and expected approved states, and denies missing or `Draft` predecessors for supported artifact writes, using representative `apply_patch`, `Edit`, and `Write` event inputs.
- [ ] VERIFY Active Codex installation guidance and plugin files contain no Claude commands, `.claude-plugin` paths, Claude hook variables, or slash-command invocations.
