# CLAUDE.md

Guidance for Claude Code working in this repository.

## What this repository contains

`spec-flow` is a Claude Code plugin, not an application. The distributable package lives in `plugins/spec-flow/` and contains Markdown skills, templates, a small Python controller, and a `PreToolUse` hook. There is no application build. Verify the package layout, the controller and hook tests, and the documented workflow.

## Architecture

Two flows and a backlog:

```text
Strategic:    constitution → design (architecture, infrastructure, structure, as applicable) → roadmap
Operational:  spec → plan → tasks → implement → review-release → finishing-branch   (one cycle per planned release, repeated)
Backlog:      deferred ideas, no approval, gates nothing
```

The strategic flow is approved once and revised by change. Each release is an explicit SemVer `vX.Y.Z` that must appear in the approved roadmap; a new need changes the roadmap first. Strategy lives in `.specs/{constitution,architecture,infrastructure,structure,roadmap}.md` as applicable. Each release lives in `.specs/release-vX.Y.Z/{spec,plan,tasks}.md`. Legacy `.specs/NNN-feature-name/` projects must migrate before new writes.

The controller is a document-approval ledger. It records explicit human approvals of exact document content, checks exact-digest dependencies, and validates document structure. It does not run, delegate, review, or track implementation. Implementation runs each task's steps with normal tools and reports the results.

The `<HARD-GATE>` block at the top of each gated `SKILL.md` must be preserved when editing it.

The `PreToolUse` hook (`plugins/spec-flow/hooks/`) checks `Edit`, `MultiEdit`, and `Write` calls. It blocks a strategic or release document whose prerequisites are not approved, and blocks writes into `.spec-flow/`. It does not block code changes.

## Plugin and marketplace layout

- `plugins/spec-flow/.claude-plugin/plugin.json` is the plugin manifest.
- `.claude-plugin/marketplace.json` at the repository root declares the marketplace and points at `./plugins/spec-flow`.
- `plugins/spec-flow/skills/<name>/SKILL.md` contains each skill and its optional `assets/` templates. Skills are discovered automatically.
- `plugins/spec-flow/hooks/hooks.json` registers the hook. It runs `${CLAUDE_PLUGIN_ROOT}/hooks/check-phase-approval.py`.
- `plugins/spec-flow/harness/` contains the controller runtime (`runtime/`), canonical document contracts (`contracts/`), and the document schema (`schemas/`). `_vendor/yaml` is bundled PyYAML.
- `plugins/spec-flow/scripts/spec-flow.py` is the controller entry point.

## Skill conventions

Each skill is `plugins/spec-flow/skills/<name>/SKILL.md` with YAML frontmatter:

- `name` matches the directory.
- `description` starts with a verb and says when the skill runs.

Templates in `assets/` define each document's canonical shape. When a shape changes, change its template. Refer to other skills by their plain name, for example "the `plan` skill".

Skills that write documents link `harness/contracts/operations.md` before any controller call.

## Scripts

- `python3 -B ${CLAUDE_PLUGIN_ROOT}/scripts/spec-flow.py --root <project> OP --input <json-file>` is the controller entry point. Supported operations: `initialize`, `digest`, `validate`, `approve`, `gate`, `hook-check`, `migrate-preview`, `migrate-apply`, `migrate-resume`.

## Releasing

Keep the version in `plugins/spec-flow/.claude-plugin/plugin.json` and in the marketplace entry identical. The current package version is `0.5.1`. Retain it unless a release bump is part of the work. A release bump and its `CHANGELOG.md` `## Release vX.Y.Z` heading go in a separate commit from feature changes. Collect work under `## Unreleased` until a release is cut.

## Cross-file conventions

- Release directories are `release-vX.Y.Z` with strict numeric SemVer. `NNN-short-description` is a legacy format for migration only.
- A document revision starts at `R00` and increments only for a substantive edit after approval. Revisions before approval stay `R00`.
- Keep `plugins/spec-flow/skills/using-spec-flow/SKILL.md`, each phase skill, and `README.md`'s workflow aligned.
- If the flow changes, update the manifest descriptions, the marketplace entry, `README.md`, the bootstrap skill, and affected skill guidance together.
- Shared controller mechanics (invocation, read-only queries, adoption, approval and revision) live in `plugins/spec-flow/harness/contracts/operations.md`. Skills link it and keep their own HARD-GATE, mode restrictions, and semantic checks.

## Canonical document encoding

New canonical documents use YAML frontmatter before the title. Legacy fenced JSON documents remain readable and keep their digests. Encoding conversion is explicit: it changes the digest and requires re-approval. Keep JSON for manifests, CLI payloads and results, and internal records. See `plugins/spec-flow/harness/contracts/canonical-contract.md`.

## Tests

Install the development tools once, outside the plugin runtime: `cd plugins/spec-flow && python3 -m pip install -r requirements-dev.txt`.

Run the tests with `cd plugins/spec-flow && python3 -m pytest -q`. Pytest reads its paths from `plugins/spec-flow/pyproject.toml`.

Run the type check with `cd plugins/spec-flow && python3 -m mypy`. It checks `harness/runtime`, `scripts`, and `hooks`, and excludes the vendored YAML and the test modules. The configuration lives in the same `pyproject.toml`.
