# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`spec-flow` is a **Claude Code plugin** — not an application. It ships prompt content, not code. There is nothing to build, run, or unit-test in the usual sense: the deliverable is a set of skills (markdown) plus two helper shell scripts. Editing this repo means editing prompts and templates.

## Architecture

The plugin enforces a seven-phase Spec-Driven Development chain, each phase gated on the previous artifact existing:

```
constitution → specify → plan → tasks → implement → converge → finishing-branch
```

Artifacts live in the **consuming project's** `.specs/` directory (not this repo's), one folder per feature: `.specs/NNN-feature-name/{spec,plan,tasks}.md`, plus a single top-level `.specs/constitution.md`. This repo's own `.specs/` is dogfooding — spec-flow used to build spec-flow.

Two side-channel skills sit outside the gate chain: `clarify` (after specify) and `analyze` (after tasks) — both recommended, never required. `backlog` parks deferred ideas in `.specs/backlog.md`; `specify` consumes and removes matching entries.

The **hard gates** are the load-bearing invariant. Each SKILL.md opens with a `<HARD-GATE>` block that must block progress until the prior artifact exists. When editing any phase skill, preserve its gate — that's what makes this "spec-driven" rather than a suggestion.

## Skill anatomy

Each skill is `skills/<name>/SKILL.md` with YAML frontmatter:

- `name` — must match the directory name.
- `description` — third person, starts with a verb, states *when* to invoke. This is the trigger the model matches on; keep it discriminating.
- `model` + `effort` — set per phase, using model **aliases** (`opus`, `sonnet`) not pinned IDs, so each phase tracks the latest release. Rationale below. Match this convention when adding a skill.

### Model & effort rationale

Two independent axes (per Anthropic's [effort docs](https://platform.claude.com/docs/en/build-with-claude/effort)): **model ≈ how capable** (reach for a bigger model on hard/ambiguous/architectural problems), **effort ≈ how thorough** (reads more files, verifies, pushes through multi-step work before checking in). A phase needing judgment wants a capable model; a mechanical phase where skipping a step is the failure mode wants high effort on a cheaper model.

| Phase | model / effort | Why |
|---|---|---|
| constitution | opus / high | Sets project-wide principles from a vague brief — high ambiguity, capability-bound; runs once per project so capability is cheap here |
| specify | opus / high | Turns a fuzzy idea into a testable spec — ambiguity-bound |
| clarify | opus / medium | Generating the *right* questions is a capability task; short + optional, so effort stays low |
| plan | opus / high | Architecture and tech choices — the textbook case for a large model |
| tasks | sonnet / high | Decomposition from an *approved* plan — mechanical enough for a smaller model, but high effort so no task or dependency is skipped |
| analyze | opus / medium | Catching subtle cross-artifact contradictions — capability-bound; read-only + optional, so effort stays low |
| implement | sonnet / medium | Executing precisely-described tasks — routine work, no reason to pay for capability |
| converge | opus / high | Judging whether code matches intent — capability-bound |
| finishing-branch | sonnet / medium | Mechanical (tests, changelog, git) but skipping a step is the risk — low capability, high thoroughness |

Optional subdirs: `assets/` holds output templates (e.g. `spec-template.md`) that the skill fills in; `scripts/` holds skill-local helpers. Templates are the canonical output shape — edit the template, not the skill's inline prose, to change document structure.

## Scripts

- `scripts/check-complete.sh <tasks.md>` — exits 0 if all `- [ ]` are checked, 1 otherwise. Used by phase gates.
- `skills/specify/scripts/next-feature-number.sh [specs-dir]` — returns the next zero-padded `NNN` by scanning existing `.specs/NNN-*` dirs.

## Releasing

Version lives in `.claude-plugin/plugin.json`. On release: bump that version, add a `CHANGELOG.md` entry. `.claude-plugin/marketplace.json` is the marketplace listing. Keep `plugin.json`, `marketplace.json`, and `README.md`'s phase table in sync when the phase set changes.

## Conventions that cross files

- Feature naming: `NNN-short-description`, kebab-case, 2–4 words describing the feature (not the implementation). Same string is the directory name and the frontmatter `name`.
- Spec versioning: frontmatter `version` starts `R00` and only increments on an edit requested *after* approval — revision loops before approval stay `R00`.
- The README, `using-spec-flow/SKILL.md`, and each phase's SKILL.md all restate the seven-phase table. A change to the phase model must land in all three.
