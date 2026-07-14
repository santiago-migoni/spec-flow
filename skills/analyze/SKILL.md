---
name: analyze
description: "Read-only cross-check of spec.md, plan.md, and tasks.md for duplication, ambiguity, coverage gaps, and constitution conflicts. Run after spec-flow:tasks, before spec-flow:implement. Recommended, never required, and never writes any file."
model: opus
effort: high
---

# Spec-Flow: Analyze

Cross-check the three core artifacts for consistency before any code is written. This is the one phase in Spec-Flow that never writes to disk.

<HARD-GATE>
`spec.md`, `plan.md`, and `tasks.md` must all exist for the current feature — if `tasks.md` is missing, stop and invoke `spec-flow:tasks` first.
</HARD-GATE>

## When to Run This Phase

- After `tasks.md` is written, before `spec-flow:implement`
- Recommended, never required — `implement`'s hard-gate does not check whether `analyze` has run

## Operating Constraint: Read-Only

Analyze never modifies `spec.md`, `plan.md`, `tasks.md`, or any other file. It only produces a report in the conversation. This is a deliberate exception to Spec-Flow's "every phase writes one artifact" principle — cross-checking read-only is the whole point of this phase.

## Process

1. **Read `spec.md`** (user stories, acceptance scenarios, edge cases, non-goals), **`plan.md`** (architecture, file structure, data model, dependencies), **`tasks.md`** (task IDs, descriptions, `[P]` markers, file paths), and **`.specs/constitution.md`** (MUST principles)
2. **Build an internal inventory** (don't print it): one entry per acceptance scenario, one entry per plan decision implying a concrete artifact, one entry per constitution MUST principle relevant to this feature, and a task-coverage map (which requirement/story each task maps to)
3. **Detect findings**:
   - Duplication — near-duplicate requirements
   - Ambiguity — vague adjectives (fast, robust, intuitive) lacking a measurable criterion; unresolved `TODO`/`[NEEDS CLARIFICATION]` markers
   - Coverage gaps — requirements with zero tasks, tasks with no mapped requirement
   - Constitution conflicts — any requirement or plan decision conflicting with a MUST principle
   - Inconsistency — terminology drift, conflicting requirements, task ordering contradictions
4. **Assign severity**: `CRITICAL` (constitution MUST violation, or a P1 story with zero task coverage), `HIGH` (conflicting/duplicate requirement, untestable acceptance criterion), `MEDIUM` (terminology drift, missing non-functional coverage), `LOW` (style, minor redundancy). Constitution conflicts are always `CRITICAL`.
5. **Report** a findings table (`ID | Category | Severity | Location | Summary | Recommendation`), a coverage summary (requirement → has task? → task IDs), and metrics (total requirements, total tasks, coverage %, counts per severity). Cap at 30 rows; summarize any overflow.
6. **Next Actions** — if any `CRITICAL` finding exists, recommend resolving it before `implement`; otherwise note the user may proceed, with optional improvement suggestions.
7. **Offer remediation** — ask "Want me to suggest concrete edits for the top issues?" Do not apply them without explicit approval.

## Behavior Rules

- Never modify any file — this is the one read-only phase in Spec-Flow
- Never hallucinate a missing section — report it as missing
- Constitution conflicts are always `CRITICAL`, never downgraded
- Zero findings is a valid, clean outcome — report it as such, don't invent issues to fill the report

## After Analysis

Tell the user the finding counts by severity and the recommended next step: "Analysis complete for `NNN-feature-name`. [N CRITICAL — resolve before implement / No CRITICAL findings — ready for `spec-flow:implement`]."
