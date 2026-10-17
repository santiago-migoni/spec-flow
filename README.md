# spec-flow

Spec-Flow is a Claude Code plugin for spec-driven development. It keeps product strategy and release decisions in your project's `.specs/` directory, and uses a small local controller to record approvals of those documents and check that each one's dependencies are still approved.

## Two flows and a backlog

**Strategic flow (predictive, approved once and revised by change):**

constitution → design (architecture, infrastructure, structure, as applicable) → roadmap

**Operational flow (agile, one cycle per planned release):**

spec → plan → tasks → implement → review-release → finishing-branch, then the next release's spec → plan → tasks → implement

Each release lives in `.specs/release-vX.Y.Z/` with its own `spec.md`, `plan.md`, and `tasks.md`. A release must appear in the approved roadmap. If something new is needed, change the roadmap and approve it first.

**Backlog** (`.specs/backlog.md`) holds deferred ideas. It has no approval and does not gate either flow.

## Layout

```text
.specs/
├── constitution.md
├── architecture.md         # when applicable
├── infrastructure.md       # when applicable
├── structure.md            # when applicable
├── roadmap.md
├── backlog.md              # optional
└── release-vX.Y.Z/
    ├── spec.md
    ├── plan.md
    └── tasks.md
```

## Skills

| Stage | Skill | Output |
| --- | --- | --- |
| Purpose and principles | `$constitution` | `.specs/constitution.md` |
| Architecture, infrastructure, structure | `$design` | applicable `.specs/{architecture,infrastructure,structure}.md` |
| Outcomes and releases | `$roadmap` | `.specs/roadmap.md` |
| Behavior and acceptance for one release | `$specify` | `release-vX.Y.Z/spec.md` |
| Ambiguities in a spec (optional) | `$clarify` | section inside `spec.md` |
| Technical approach and phases | `$plan` | `release-vX.Y.Z/plan.md` |
| Executable tasks | `$tasks` | `release-vX.Y.Z/tasks.md` |
| Consistency check (optional, read-only) | `$analyze` | conversation report |
| Deferred ideas | `$backlog` | `.specs/backlog.md` |
| Build the approved tasks | `$implement` | code changes and verification results |
| Review a finished release | `$review-release` | conversation report: acceptance, feedback, outcomes |
| Integrate the reviewed branch | `$finishing-branch` | merge, pull request, or kept branch, on the user's choice |
| Routing and status | `$using-spec-flow` | next step and owner |

## Approvals

Approve documents in order: constitution → design (applicable parts) → roadmap → release spec → release plan → release tasks. Each approval is recorded against the exact content and its dependencies. A change to any approved document invalidates the approvals that pinned it; re-approve the changed document and the dependents that depend on it.

Approval is a human decision. The controller records it and checks it; it does not decide what to approve.

## Controller

```sh
python3 -B <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>
```

Supported operations: `initialize`, `digest`, `validate`, `approve`, `gate`, `hook-check`, `migrate-preview`, `migrate-apply`, `migrate-resume`. The [shared operations contract](plugins/spec-flow/harness/contracts/operations.md) documents each one.

The controller does not run, delegate, or review implementation. There are no leases, profiles, or per-phase review gates: `$implement` runs each task's steps with normal tools and reports the verification results.

An optional `PreToolUse` hook (`plugins/spec-flow/hooks/`) checks `Edit`, `MultiEdit`, and `Write` calls. It blocks changes to a strategic or release document whose prerequisites are not approved, and blocks writes into `.spec-flow/`. It does not block code changes.

## Adoption and migration

On a new project, run `initialize` once before the first approval. A project with legacy `.specs/NNN-feature-name/` folders must migrate first: `migrate-preview`, human review, then `migrate-apply`. See the [migration contract](plugins/spec-flow/harness/contracts/migration.md). Migration imports approvals only; it does not import execution history.

## Install from GitHub marketplace

In Claude Code:

```text
/plugin marketplace add santiago-migoni/spec-flow
/plugin install spec-flow@spec-flow
```

Start a new session to load the installed skills. A test copy should use a separate marketplace name so it does not replace an existing installation.

## Requirements

Python 3 (bundled pure-Python PyYAML; no other installation). Git is required for the migration snapshot.

## License

GNU AGPLv3 — see [LICENSE](LICENSE).
