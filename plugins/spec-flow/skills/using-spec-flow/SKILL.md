---
name: using-spec-flow
description: "Use when entering or resuming Spec-Flow, asking for project status, or choosing the next document or delivery step."
---

# Spec-Flow: Using Spec-Flow

<HARD-GATE>
Before writing any Spec-Flow document, check the project: run `initialize` for a new unadopted project, and stop before writing if legacy `.specs/NNN-name/` folders exist, following the `migrate-preview` → human review → `migrate-apply` flow in the [migration contract](../../harness/contracts/migration.md). Before writing a document, run its `gate`; a failed gate blocks that document. Do not approve on the user's behalf.
</HARD-GATE>

## Two flows

Spec-Flow has two flows, plus a backlog.

**Strategic flow (predictive, approved once and revised by change):**

constitution → design (applicable architecture, infrastructure, and structure) → roadmap

Strategy lives in `.specs/constitution.md`, `.specs/architecture.md`, `.specs/infrastructure.md`, `.specs/structure.md`, and `.specs/roadmap.md`. Recommended design order is architecture → infrastructure → structure, and only the parts that apply to the project are written.

**Operational flow (agile, one cycle per planned release):**

spec → plan → tasks → implement → review-release → finishing-branch, then the next release's spec → plan → tasks → implement …

Each cycle lives in `.specs/release-vX.Y.Z/` with `spec.md`, `plan.md`, and `tasks.md`. A release is planned in the roadmap. If something new is needed, change the roadmap and approve it first; then write the release's spec and continue.

**Backlog:** `.specs/backlog.md` holds deferred ideas. It has no approval and does not gate the other flows. An item becomes a spec only when it is picked up for a release.

## Routing

| Request | Skill |
| --- | --- |
| Purpose, principles, boundaries | `constitution` |
| Architecture, infrastructure, or structure decisions | `design` |
| Priorities, outcomes, releases, selection | `roadmap` |
| Behavior and acceptance for one release | `specify` |
| Technical approach and phases | `plan` |
| Executable tasks | `tasks` |
| Deferred ideas | `backlog` |
| Build the approved tasks | `implement` |
| Review a finished release against its criteria and feedback | `review-release` |
| Integrate a reviewed release branch, on the user's explicit choice | `finishing-branch` |

## Approval order

constitution → design (applicable parts) → roadmap → release spec → release plan → release tasks → implement.

Each approval is recorded for the exact content and its dependencies. A change to any approved source invalidates the approvals that depend on it; re-approve the changed document and the dependents that pinned it.

## Consultation

A status question or review reads files and runs `gate` or `validate`. It writes nothing: no approval, migration preview, or report file.

## Migration

A legacy project with `.specs/NNN-name/` folders cannot be written to until it is migrated. See the [migration contract](../../harness/contracts/migration.md).

## Operations

Before invoking `spec-flow.py`, read the [shared controller operations](../../harness/contracts/operations.md). The controller only records approvals and checks dependencies; it does not run or review implementation work.
