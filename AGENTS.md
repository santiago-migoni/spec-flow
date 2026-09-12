# AGENTS.md

Guidance for Codex working in this repository.

## What this repository contains

`spec-flow` is a Codex plugin, not an application. The distributable package lives in `plugins/spec-flow/` and contains Markdown skills, templates, scripts, and a Codex hook. There is no application build or unit-test suite; verify changes against the package format, task acceptance criteria, scripts, and documented workflows.

## Architecture

The plugin guides a seven-phase Spec-Driven Development chain:

```text
constitution → specify → plan → tasks → implement → converge → finishing-branch
```

The `clarify` and `analyze` skills are recommended side channels; `backlog` records deferred ideas. Feature artifacts belong to the consuming project's `.specs/` directory: `.specs/NNN-feature-name/{spec,plan,tasks}.md`, plus `.specs/constitution.md` and optionally `.specs/backlog.md`.

The hard gates are load-bearing. Each gated `SKILL.md` starts with a `<HARD-GATE>` block and checks its predecessor artifact before writing or implementing. Preserve the prose gates when editing a skill. The optional Codex `PreToolUse` hook only reinforces approval for supported local patch writes to gated `.specs` artifacts; it does not intercept skill selection or every write path, and Codex runs it only after the user trusts the hook definition.

## Plugin and marketplace layout

- `plugins/spec-flow/plugin.json` is the portable Agent Plugins manifest. OpenAI-specific hook configuration belongs under `extensions.com.openai`.
- `plugins/spec-flow/skills/<name>/SKILL.md` contains each skill and its optional `assets/` or `scripts/` resources.
- `plugins/spec-flow/hooks/hooks.json` registers the Codex hook; its Python handler is in the same `hooks/` directory.
- `plugins/spec-flow/scripts/check-complete.sh` checks task completion.
- `.agents/plugins/marketplace.json` declares the repository marketplace. The `spec-flow` entry uses the GitHub `git-subdir` source at `https://github.com/santiago-migoni/spec-flow.git` and package path `./plugins/spec-flow`. Stable releases use ref `main`; a pre-release branch uses its own ref for both the marketplace and package, then returns to `main` before `v1.0.0`.

## Skill conventions

Each skill is `plugins/spec-flow/skills/<name>/SKILL.md` with YAML frontmatter:

- `name` matches the skill directory.
- `description` starts with a verb and clearly defines when the skill should run.
- `name` and `description` are required for Codex skill discovery. Keep skill frontmatter limited to Codex-supported metadata.

Optional subdirectories hold skill-local materials: `assets/` contains output templates; `scripts/` contains skill helpers. Templates define the canonical output shape; change the template when that shape changes.

When referring to another skill in user guidance, use its Codex name or `$<skill-name>` invocation.

## Scripts

- `plugins/spec-flow/scripts/check-complete.sh <tasks.md>` exits 0 when every task checkbox is checked and 1 otherwise.
- `plugins/spec-flow/skills/specify/scripts/next-feature-number.sh [specs-dir]` returns the next zero-padded three-digit feature number.

## Releasing

The plugin version is `plugins/spec-flow/plugin.json`. Keep the version at `0.9.0` unless a release version bump is explicitly part of the work; pre-release validation may use a SemVer prerelease such as `0.9.0-beta`. A release bump and its `CHANGELOG.md` `## Release vX.Y.Z` heading belong in a separate commit from the feature changes. Collect work in `## Unreleased` until a release is cut.

## Cross-file conventions

- Feature directories use `NNN-short-description`: three-digit number, kebab-case, and two to four words describing the feature.
- Spec version starts at `R00`; increment only for an edit requested after approval. Revision loops before approval remain `R00`.
- Keep `plugins/spec-flow/skills/using-spec-flow/SKILL.md`, each phase skill, and `README.md`'s seven-phase table aligned.
- If the phase chain changes, update the manifest description, marketplace entry, README, bootstrap skill, and affected skill guidance together.
