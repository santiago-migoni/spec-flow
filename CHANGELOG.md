# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] — 2026-06-30

### Added

- Seven-phase spec-driven development workflow: `constitution → specify → plan → tasks → implement → converge → finishing-branch`
- Hard gates between phases — each phase requires the previous artifact to exist before it can run
- All artifacts versioned in `specs/` alongside the codebase
- `spec-flow:constitution` — creates `specs/constitution.md` with project-wide principles, tech stack, and constraints (created once per project)
- `spec-flow:specify` — creates `specs/NNN-feature/spec.md` with user stories, acceptance scenarios, edge cases, and open questions
- `spec-flow:plan` — creates `specs/NNN-feature/plan.md` with approach, architecture, file structure, data model, and API contracts
- `spec-flow:tasks` — creates `specs/NNN-feature/tasks.md` with atomic task list, phase markers, and verification checklist
- `spec-flow:implement` — executes tasks one by one, marks each complete, verifies acceptance scenarios against `spec.md`
- `spec-flow:converge` — append-only gap analysis (missing, partial, contradicts, unrequested) with severity levels
- `spec-flow:finishing-branch` — verifies tests, updates `CHANGELOG.md`, and presents merge/PR/keep/discard options
- `spec-flow:using-spec-flow` — bootstrap skill that explains the full workflow and hard gates
- Automatic feature numbering via `scripts/next-feature-number.sh`
- Shared `scripts/check-complete.sh` for verifying all tasks are checked off before finishing
- Output templates in `assets/` for each phase (constitution, spec, plan, tasks)
- Ecosystem composition with Ponytail and RTK — both activate automatically if installed, no configuration needed
- Claude Desktop installation via `.plugin` archive
- Claude Code CLI installation via `claude plugin marketplace add`
