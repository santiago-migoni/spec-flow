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

**Before writing anything to disk**, output the findings table:

```
## Convergence Findings

| ID | Gap Type | Severity | Source | Evidence | Remaining Work |
|----|----------|----------|--------|----------|----------------|
| F1 | missing  | HIGH     | US1/AC2 | No input validation found in src/auth.ts | Add validation per acceptance scenario |

**Checked**: N acceptance scenarios, M plan decisions, K constitution principles
**Findings**: X missing, Y partial, Z contradicts, W unrequested
```

Ask the user to confirm before appending tasks, unless there are zero findings.

### 5. Append Convergence Tasks (or report clean)

**If there are findings:**

1. Scan all task IDs in `tasks.md`; let `M` be the highest. Let `N` be highest phase number + 1.
2. Append to the end of `tasks.md`:

```markdown
## Phase N: Convergence

- [ ] T{M+1} <imperative action> per <source-ref> (missing)
- [ ] T{M+2} <imperative action> per <source-ref> (partial)
```

Rules:
- Order: CRITICAL first, then HIGH, MEDIUM, LOW
- Each task: imperative verb, exact file path if known, source reference, gap type in parentheses
- Constitution violations are always first and labeled CRITICAL
- Never reuse or modify existing task IDs

**If there are zero findings:**

- Do not modify `tasks.md`
- Update `Status` in `spec.md` from `Draft` to `Converged` and set today's date
- Report: "Converged — the implementation satisfies the spec, plan, and constitution."

### 6. Handoff

**On tasks appended**: state how many tasks were added under Phase N, then tell the user to run `spec-flow:implement` to complete them. A follow-up converge run will find fewer or no items.

**On converged**: the feature is done. Tell the user: "Ready to run `spec-flow:finishing-branch`."
