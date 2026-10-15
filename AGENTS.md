# AGENTS.md

Guidance for Codex working in this repository.

## What this repository contains

`spec-flow` is a Codex plugin, not an application. The distributable package lives in `plugins/spec-flow/` and contains Markdown skills, templates, a Python controller, and a Codex hook. There is no application build. Verify the package format, task acceptance criteria, controller and hook tests, and the documented workflow. E7 native evaluation and E8 isolated installation passed; evidence is in docs/implementation/harness-progress.md and harness-distribution.md. These results apply to the evaluated host and development candidate, not a published release.

## Architecture

The plugin is moving to a strategy → release → verified implementation chain:

```text
constitution → applicable shared design → roadmap → specify → plan → tasks → implement → converge → review-release → finishing-branch
```

Shared design means architecture, structure, and infrastructure documents only where applicable; the roadmap records N/A with a reason otherwise. The `clarify` and `analyze` skills are recommended side channels; `backlog` records deferred ideas. Strategy artifacts belong in `.specs/{constitution,architecture,structure,infrastructure,roadmap}.md` as applicable. Each explicit SemVer release uses `.specs/release-vX.Y.Z/{spec,plan,tasks}.md` and may contain several stories. Legacy `.specs/NNN-feature-name/` projects must migrate before new writes.

The hard gates are load-bearing. Each gated `SKILL.md` starts with a `<HARD-GATE>` block. Preserve those blocks when editing. The controller's registry approval receipts, dependency digests, execution authorization, and evidence determine release gates; Markdown status and checkboxes are generated views, not authority. Production execution requires an isolated linked Git worktree, writable common-directory ownership registry, native Codex delegation, and readable host session logs. The actual orchestrator is attested Sol high, the single active implementer is Luna high, and a distinct Sol high session reviews the phase. The controller does not launch models or silently fall back to another profile. Default execution scope is one authorized phase; a wider explicit authorization is reused only within its scope, with review and commit between phases. Reconcile active agents and worktree changes before retrying after interruption.

The optional Codex `PreToolUse` hook consults the shared controller validators and active execution registry for supported patch/Edit/Write inputs. It resolves the project/worktree registration without relying on a feature branch name. It does not intercept skill selection or every write path, or replace the skill and controller gates. Codex runs it only after the user trusts its definition.

## Plugin and marketplace layout

- `plugins/spec-flow/plugin.json` is the canonical portable Agent Plugins manifest. Keep `plugins/spec-flow/.codex-plugin/plugin.json` as its Codex compatibility fallback and mirror the identity and OpenAI-specific settings. Hook paths in both manifests resolve from the plugin root.
- `plugins/spec-flow/skills/<name>/SKILL.md` contains each skill and its optional `assets/` or `scripts/` resources.
- `plugins/spec-flow/harness/` contains canonical contracts, native adapter guidance, role instructions, and the deterministic controller runtime.
- `plugins/spec-flow/hooks/hooks.json` registers the limited Codex hook; its Python handler is in the same `hooks/` directory.
- `.agents/plugins/marketplace.json` declares the repository marketplace. The `spec-flow` entry uses the GitHub `git-subdir` source at `https://github.com/santiago-migoni/spec-flow.git` and package path `./plugins/spec-flow`. Stable releases use ref `main`; a pre-release branch uses its own ref for both the marketplace and package, then returns to `main` before its stable release.

## Skill conventions

Each skill is `plugins/spec-flow/skills/<name>/SKILL.md` with YAML frontmatter:

- `name` matches the skill directory.
- `description` starts with a verb and clearly defines when the skill should run.
- `name` and `description` are required for Codex skill discovery. Keep skill frontmatter limited to Codex-supported metadata.

Optional subdirectories hold skill-local materials: `assets/` contains output templates; `scripts/` contains skill helpers. Templates define the canonical output shape; change the template when that shape changes. When referring to another skill in user guidance, use its Codex name or `$<skill-name>` invocation.

## Scripts

- `python3 plugins/spec-flow/scripts/spec-flow.py --root <project> OP --input <json-file>` is the portable controller entry point.
- `plugins/spec-flow/scripts/check-complete.sh <tasks.md>` queries the controller for evidence-based release completion; manual checkboxes do not establish completion.
- Releases are selected explicitly from the approved roadmap; no automatic feature-number or version-selection helper is used.

## Releasing

Keep the version identical in `plugins/spec-flow/plugin.json` and `plugins/spec-flow/.codex-plugin/plugin.json`. The current release is `2.0.0`; retain it unless a release version bump is explicitly part of the work. A release bump and its `CHANGELOG.md` `## Release vX.Y.Z` heading belong in a separate commit from the feature changes. Collect work in `## Unreleased` until a release is cut. E7 evaluation and a fresh installed-package test must pass before claiming the new workflow is ready for release; testing must use a separate marketplace identity so it does not replace the user's existing installation.

## Cross-file conventions

- Release directories use `release-vX.Y.Z` with strict numeric SemVer. `NNN-short-description` is a legacy source format for migration, not a new release path.
- Document revision starts at `R00`; increment only for an edit requested after approval. Revision loops before approval remain `R00`.
- Keep `plugins/spec-flow/skills/using-spec-flow/SKILL.md`, each phase skill, and `README.md`'s workflow table aligned.
- If the phase chain changes, update the manifest description, marketplace entry, README, bootstrap skill, and affected skill guidance together.
