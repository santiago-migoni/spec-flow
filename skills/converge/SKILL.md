---
name: converge
description: "Assess the current codebase against the feature's spec, plan, and tasks. Classify gaps, then append any remaining work as new tasks to tasks.md so implement can complete it. Use this after implement has run at least once to close the loop between artifacts and code."
model: opus
effort: high
---

# Spec-Flow: Converge

Close the gap between what the artifacts say should exist and what the code actually contains. This phase runs after `implement` and produces either a clean confirmation or new convergence tasks.

<HARD-GATE>
Before proceeding:
1. `.specs/NNN-feature-name/spec.md` must exist
2. `.specs/NNN-feature-name/plan.md` must exist
3. `.specs/NNN-feature-name/tasks.md` must exist and have been through at least one `implement` pass
</HARD-GATE>

## Core Constraint: Append-Only

Converge has exactly one write action: appending a `## Phase N: Convergence` section to `tasks.md`.

It must NOT:
- Modify `spec.md` or `plan.md`
- Rewrite, renumber, or delete existing tasks
- Write or modify any application code

When the codebase already satisfies everything, leave `tasks.md` byte-for-byte unchanged and report clean.

This holds even across the same-invocation re-check described in step 6: re-running the assessment after fixes land in the same conversation is still bounded to the same two write paths (append a new `## Phase N+1: Convergence` section, or set `Status: Converged`) — converge never applies a fix itself and never auto-invokes `implement` to make that happen.

## Process

### 1. Load Artifacts

Read the following — load only what's needed for assessment, not the full text verbatim:

**From `spec.md`**: user stories, acceptance scenarios, edge cases, explicit non-goals.

**From `plan.md`**: architecture decisions, file structure, data model, API contracts, dependencies listed.

**From `tasks.md`**: all existing task IDs (to determine next ID), the highest phase number (to determine next phase).

**From `.specs/constitution.md`**: MUST principles that impose buildable obligations.

### 2. Build the Intent Inventory

Construct an internal map (do not print this):
- One entry per acceptance scenario (`US1/AC1`, `US1/AC2`, `US2/AC1`…)
- One entry per plan decision that implies a concrete artifact (file, endpoint, data model field)
- One entry per constitution MUST principle relevant to this feature

Derive the code scope from file paths named in `plan.md` and `tasks.md`. Bound the assessment to those files — do not invent scope beyond what the artifacts define.

### 3. Assess and Classify Findings

For each inventory item, inspect the current code. Record a finding only where a gap exists.

**Gap types:**

| Type | Meaning |
|---|---|
| `missing` | Required work is entirely absent from the code |
| `partial` | Work exists but does not fully satisfy the requirement |
| `contradicts` | Code conflicts with stated intent or a constitution MUST principle |
| `unrequested` | Code exists that no artifact called for — flag for awareness only |

**Severity:**

| Severity | Criteria |
|---|---|
| `CRITICAL` | Violates a constitution MUST principle, or blocks a P1 user story entirely |
| `HIGH` | Missing or partial gap on a core acceptance scenario or plan decision |
| `MEDIUM` | Partial gap on a secondary requirement, or unrequested addition without clear justification |
| `LOW` | Minor polish, edge case gap, or low-risk unrequested addition |

**Edge cases:**
- If there is little or no code yet, treat the full scope as `missing` rather than failing.
- If nothing remains, produce zero findings.

### 4. Present Findings Summary

**Before writing anything to disk**, output the findings table using `assets/convergence-report-template.md` as the format.

Ask the user to confirm before appending tasks, unless there are zero findings.

### 5. Append Convergence Tasks (or report clean)

**If there are findings:**

1. Scan all task IDs in `tasks.md`; let `M` be the highest. Let `N` be highest phase number + 1.
2. Append to the end of `tasks.md` using `assets/convergence-report-template.md`'s "Appended to tasks.md" block as the format.

Rules:
- Order: CRITICAL first, then HIGH, MEDIUM, LOW
- Each task: imperative verb, exact file path if known, source reference, gap type in parentheses
- Constitution violations are always first and labeled CRITICAL
- Never reuse or modify existing task IDs

**If there are zero findings:**

- Do not modify `tasks.md`
- Update `Status` in `spec.md`'s document-control table to `Converged` and set today's date
- Report: "Converged — the implementation satisfies the spec, plan, and constitution."

### 6. Handoff

**On tasks appended**: state how many tasks were added under Phase N. Offer a re-check within this same invocation: once the fixes are applied in this same conversation (by the user or by `implement`), re-run the assessment (steps 2-5) against the updated code — clean re-check sets `Status: Converged` per step 5's zero-findings path; residual gaps append another `## Phase N+1: Convergence` per step 5's findings path. This re-check introduces no write beyond those two existing paths — converge still never applies fixes itself and never auto-invokes `implement`.

**If the fixes are not applied in this same conversation** (the user leaves, or defers): converge cannot re-check work that hasn't happened. Report the appended tasks and stop there, same as today — tell the user to run `spec-flow:implement` to complete them, then a follow-up `spec-flow:converge` run will find fewer or no items. The single-pass re-check is the happy path, not an obligation.

**On converged** (whether on the first assessment or after a same-invocation re-check): the feature is done. Tell the user: "Ready to run `spec-flow:finishing-branch`."
