---
name: converge
description: "Assess a committed release against approved acceptance and shared decisions, then route residual work to its canonical source."
---

# Spec-Flow: Converge

<HARD-GATE>
Require an adopted release with valid spec, plan, and tasks; current registry approvals; at least one verified implementation pass; and reviewed phase commits for all phases claimed complete. Run the controller gate and evidence-based `complete` query; proceed to technical convergence only when `technical_complete` is true. The query also reports `release_review_pending` and `audit_pending` for the later closure steps. Checked boxes or a Markdown Converged label alone do not satisfy this gate.
</HARD-GATE>

## Purpose and boundaries

Assess the integrated release against approved behavior, quality, completion conditions, and shared decisions. Task completion is necessary; it does not by itself demonstrate usable, coherent release behavior. Read the approved scope, edge cases, non-goals, and plan deliverables. Inspect only relevant code and interfaces within that scope.

Use [the report template](assets/convergence-report-template.md) for conversation output. Assessment and reporting do not change decision content or execution state. Do not write application code, retry a task, or spawn Luna from this skill. Route required work to its canonical owner; this skill never fixes the gap itself.

## Assessment context

Identify the adopted release and execution run, approved document IDs/revisions and source pins, current registry approvals, evaluated SHA, reviewed phase commits, and available task/step evidence. Reference applicable constitution, architecture, infrastructure, and structure decisions actually used; do not require every shared document or introduce a fixed design dependency chain. Record relevant environment, configuration, data, and inspection conditions.

Run the read-only `gate` for converge and the release's `complete` query using [the execution contract](../../harness/contracts/execution.md). Require `gate.ready` and `complete.technical_complete` to be true. A missing field, including a completion response with no execution run, does not satisfy that requirement. If entry fails, report Not eligible, quote actual reasons, and identify the owning prerequisite without claiming to have assessed acceptance. Preserve missing/unavailable results rather than inventing controller values. `release_review_pending` and `audit_pending` describe later closure work and do not independently prevent this assessment.

## Acceptance coverage

Include every AC exactly once in canonical spec order under its actual owning story. Reference contributing tasks/phases and existing final-verification step IDs. Keep partial contributions explicit: an enabling task can close while its referenced AC remains unsatisfied. Nominal ID coverage, checked boxes, or all tasks completed cannot establish final acceptance.

For each AC, compare its full approved behavior and examples, including relevant success/error cases, with observed results. Follow referenced NFRs to their approved targets, conditions, and measurement methods; report the observed comparison. Review approved completion and quality obligations from the constitution, spec, plan, and applicable shared decisions. These tables are assessment views, not new definitions or manually maintained acceptance records.

## Integrated assessment

Examine relevant end-to-end behavior, component interfaces, compatibility, errors, and regressions across the delivered increments. Check implementation against applicable shared responsibilities, placement rules, and operating constraints. Evaluate documentation, configuration, packaging, migration, observability, and recovery only where approved delivery/completion obligations make them applicable. Use the agreed quality thresholds and conditions; do not introduce a universal checklist or new requirements at convergence.

State applicability and evidence for each examined aspect. N/A needs an approved-scope reason; it cannot discard an approved AC or other applicable obligation. Propose new requirements through their owning source rather than silently treating them as existing acceptance failures.

## Evidence sufficiency

Use the controller's actual verification results and current code, not an agent's PASS claim. The controller establishes current approvals, task evidence, and reviewed commits; `technical_complete=true` is the prerequisite for this semantic assessment, not its conclusion. Compare expected and observed results, confirm relevant cases actually executed, and cite task/step receipts, outputs, measurements, inspections, and commits with enough conditions to explain what they demonstrate. A passing suite without the required behavior or NFR conditions is insufficient.

Reuse evidence that remains current and relevant; a new report alone does not require rerunning checks. If evidence must be produced or refreshed, hand it to `$implement` under the existing verification/recovery controls. Refreshing completed-task evidence does not reopen implementation or certify code that differs from the reviewed phase tree.

Use Satisfied, Gap, or Not verifiable for assessed coverage. Missing or insufficient evidence for an approved obligation is Not verifiable and requires a finding; it cannot become Satisfied through an assumption. Explain limitations that do not affect an obligation without inventing a failure.

## Findings and canonical routing

Classify actual gaps as missing, partial, contradictory, or unrequested. Unrequested means implemented behavior outside approved boundaries, not a suggested optional improvement. For each finding, identify the approved source, expected versus observed condition, evidence or missing demonstration, consequence, justified severity, and exact proposed change/destination. A constitution MUST violation is CRITICAL. Every outstanding finding, including LOW, prevents a clean result. Separate optional opportunities from findings; suggestions neither expand scope nor automatically become tasks.

| Required change | Canonical owner and next step |
| --- | --- |
| Complete implementation or verification without changing approved behavior/solution | `$tasks`, then `$implement` under applicable authorization |
| Change behavior or acceptance | `$specify` |
| Change technical solution, phases, or delivery approach | `$plan` |
| Change a shared design or principle | `$architecture`, `$infrastructure`, `$structure`, or `$constitution`, as applicable |
| Change release priorities/scope or defer an optional idea | `$roadmap` or `$backlog`, as appropriate |

For an implementation gap, propose a concrete canonical `tasks.md` change with stable ID, phase, story and AC references, dependencies, steps, expected verification, closure, and file scope. Do not create a second editable gap list. Do not hide an approved obligation in backlog; deferral needs an approved scope change at its owner. Show the exact proposed decision change before it is applied through the owning skill. An exact recommendation accepted verbatim can serve as the user's approval; open-ended wording needs review. Revision and approval changes affect only dependent decisions that actually adopt the new base.

## Follow-up and recovery

When residual work is approved and added to its canonical source, hand execution back to `$implement` under the appropriate authorization. Reconcile active agents, worktree changes, source approvals, and execution state first. Changed approved sources require explicit adoption of affected pins/approvals and the authorized abandon/new-run recovery path; do not reopen committed phases by assumption. Reuse completed evidence only while its exact contracts, source pins, checks, and code fingerprints remain applicable. Use new IDs for new work and preserve unchanged IDs/history.

A subsequent convergence pass checks entry again and assesses the updated release, reusing valid unaffected evidence while examining changed behavior, interfaces, and relevant regressions. Do not assume that a proposed task or an earlier clean report authorizes implementation or still proves convergence after changes.

## Outcome and handoff

Report one conversational conclusion, distinct from controller fields:

- Not eligible: an entry condition failed; acceptance assessment did not proceed.
- Technical convergence not confirmed: entry passed, but a gap or insufficient evidence remains.
- Technical convergence confirmed: entry passed, every AC and applicable approved obligation is demonstrated, and zero findings remain.

If no gaps remain, leave `tasks.md` and approved decision content unchanged. Cite the actual `complete.technical_complete` result, release/run, reviewed phase commits, and current evidence. Do not mark the spec Converged, write a separate convergence document or generated closure note, or call `release-review` here. Hand off to `$review-release`, which records the combined derived technical and impact outcome after this assessment. Technical convergence does not prove measured impact or authorize integration, publication, deployment, or a version bump.
