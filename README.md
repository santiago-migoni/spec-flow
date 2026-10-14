# spec-flow

Spec-Flow is a Codex plugin for release-centered Spec-Driven Development. It records product strategy and release decisions in a consuming project's `.specs/` directory, then uses a local controller to validate document dependencies, approval receipts, execution evidence, and recovery.

The intended path is **strategy → release → verified implementation**. The strategy documents are the constitution, applicable shared architecture/structure/infrastructure decisions, and roadmap. Each explicit SemVer release has its own spec, plan, and tasks. A release may contain several stories or features.

## Workflow

| Stage | Skill | Canonical artifact or result | Gate |
| --- | --- | --- | --- |
| Purpose and boundaries | `$constitution` | `.specs/constitution.md` | Human direction for unknown business decisions |
| Shared system design | `$architecture`, `$structure`, `$infrastructure` | Applicable `.specs/*.md` documents | Constitution and relevant prior decisions approved; roadmap records N/A with a reason when a document does not apply |
| Release sequence | `$roadmap` | `.specs/roadmap.md` | Approved strategy; explicit `vX.Y.Z` releases |
| Release behavior | `$specify` | `.specs/release-vX.Y.Z/spec.md` | Release selected from the approved roadmap |
| Solution | `$plan` | `.specs/release-vX.Y.Z/plan.md` | Approved release spec and applicable design |
| Executable work | `$tasks` | `.specs/release-vX.Y.Z/tasks.md` | Approved plan; stable tasks, steps, acceptance links, file scope, and checks |
| Execution | `$implement` | Evidence-backed tasks, independent phase review, and phase commits | Current approval registry, explicit execution authorization, and native host prerequisites |
| Technical closure | `$converge` | Findings or derived closure in the release spec | Current task evidence and reviewed phase commits |
| Outcome review | `$review-release` | Derived review in the release spec | Technical convergence; impact may still be pending measurement |
| Integration | `$finishing-branch` | Audit checkpoint and authorized integration action | Release review and evidence-based completion |

`$clarify` and `$analyze` are recommended side channels for ambiguity and consistency; `$backlog` parks deferred ideas. `$using-spec-flow` finds the next authorized step. The technical design documents are applicable as needed, not a mandatory architecture → structure → infrastructure ladder.

```text
.specs/
├── constitution.md
├── architecture.md         # when applicable
├── structure.md            # when applicable
├── infrastructure.md       # when applicable
├── roadmap.md
├── backlog.md              # optional
└── release-v2.0.0/
    ├── spec.md
    ├── plan.md
    └── tasks.md
```

## Adoption and approvals

On a new project, initialize the controller before writing canonical documents. A project with legacy `.specs/NNN-feature-name/` folders must run the migration preview and apply workflow before new Spec-Flow writes. Migration requires a committed snapshot of the exact originals, explicit feature-to-release mapping, and reviewed candidate documents. Old `Status: Approved` text and checked boxes do not become authority or verification by themselves; only identifiable, verifiable historical records can be imported. See [migration.md](plugins/spec-flow/harness/contracts/migration.md).

Use the portable CLI as `python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>`. The controller implements initialization, migration, validation, digest, approval, gate, and status operations, plus an event-backed execution protocol. Approval receipts pin normalized decision content and its dependency closure; updates to derived progress alone do not invalidate approval. An exact recommendation already accepted by the user can supply approval; changed decisions require review of the affected source and dependent decisions. Urgency and a document's displayed status do not waive a failed gate. Execution authorization is scoped to a release and phase or set of phases; it does not authorize merge, push, publication, or deployment.

For a new project, save `{}` as an input JSON file and call `initialize`. After drafting a document, call `validate` with `{"path":".specs/constitution.md"}` or the corresponding project-relative path, then obtain its approval before dependent work. The [canonical contract](plugins/spec-flow/harness/contracts/canonical-contract.md) defines the document shape and dependency rules.

## Native Codex execution

The runtime uses Python standard library and POSIX file locks (`fcntl`); Windows is not currently supported. Verification in this development environment uses Python 3.14.4 and Git 2.54.0. Production implementation requires an isolated linked Git worktree, writable Git common-directory ownership registry, native Codex delegation tools, and readable host session logs. The actual orchestrator must be attested **Sol high**; one **Luna high** implementer works on a scoped task at a time; a distinct **Sol high** reviewer checks the integrated phase before its commit. Python enforces contracts and records evidence; it does not launch models or infer their identity from a supplied model name. If a host capability or attestation is unavailable, execution stops with a diagnostic and no automatic model substitution.

The default invocation covers one authorized phase. Each task needs current verification against the actual worktree and Sol review. The first Luna attempt may receive at most two targeted corrections. A phase closes only after an independent review of its stable staged tree and a matching validated commit. On interruption, inspect the active native agent and worktree, then resume or reconcile the existing attempt before retrying; a lost final message does not justify replay. The controller keeps compact audit records and an audit checkpoint after the last code phase. See the [execution contract](plugins/spec-flow/harness/contracts/execution.md) and [Codex adapter](plugins/spec-flow/harness/adapters/codex/README.md).

The bundled `PreToolUse` hook is a limited reinforcement for supported `apply_patch`/`Edit`/`Write` inputs after the user trusts it. The handler consults the same release validators and execution registry as the controller, resolves the Git common-directory ownership record, and checks supported write paths against the active task scope without relying on the branch name. It does not select skills, inspect all write methods, or replace the controller's release approval and evidence gates. Treat a hook allow as no proof of authorization.

The development candidate passed native fresh-project and migration evaluations, interruption and failed-correction checks, and a separate installed-package test. See the [evaluation record](docs/implementation/harness-progress.md) and [distribution evidence](docs/implementation/harness-distribution.md). **2.0.0 is prepared locally on main**, including the final review fixes (114 plugin tests and 9 hook tests). The native and installed-package evaluations predate those fixes. Tagging and publication remain pending; the published version is still **1.1.0**. The measurements do not establish time or cost savings.

## Install from GitHub marketplace

The stable marketplace points to GitHub `main`:

```bash
codex plugin marketplace add santiago-migoni/spec-flow --ref main
codex plugin add spec-flow@spec-flow
```

This installs the package from the marketplace source, not from a local checkout. Start a new Codex chat to discover the installed skills. The local test package should use a separate, uniquely named marketplace so it cannot replace an existing installation. A release version change and its changelog heading are separate from feature changes.

## Ecosystem

Spec-Flow can coexist with [Ponytail](https://github.com/DietrichGebert/ponytail) and [RTK](https://github.com/rtk-ai/rtk); neither is required.

## License

GNU AGPLv3 — see [LICENSE](LICENSE).
