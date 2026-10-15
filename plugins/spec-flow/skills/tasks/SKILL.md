---
name: tasks
description: "Decompose an approved release plan when preparing or revising executable tasks for that release."
---

# Spec-Flow: tasks

<HARD-GATE>
Require current registry approval of the release plan and its spec/strategy dependencies. Run gate for tasks; do not write tasks against a stale plan.
</HARD-GATE>

Read the current approved plan/spec, applicable shared decisions, and repository evidence. Inspect actual files, tools, and check selectors. Write `.specs/release-vX.Y.Z/tasks.md` using [the tasks template](assets/tasks-template.md). Use all ten sections for bases, granularity, task map, sequence, file scope, coverage, verification, blockers/readiness, closure, and refinement/approval. Ask for missing human decisions and keep unknown facts or estimates explicit.

## Decompose into executable tasks

The contract owns the canonical executable task list. Keep kind tasks, id TASKS-X.Y.Z, revision R00 initially, and an exact-digest dependency on plan.md. Preserve the schema: each task has stable id, phase, story, nonempty acceptance IDs, depends_on, explicit files, ordered steps, and closure. Use T- followed by at least three digits; each unique step ID uses its task ID plus a numeric suffix of at least three digits. Phase and story IDs must exist; every linked AC must belong to that task's story. Keep one active release, which may contain several stories/features.

Each task is specific, measurable, achievable, relevant, and bounded, with a concrete contribution that can be implemented, checked, and reviewed clearly. Group by story and actual prerequisites within plan phases. Justify enabling work and label partial contributions; technical tasks need not deliver a whole story independently. Split work that bundles unrelated outcomes or is too large/uncertain to verify clearly. Use estimates only with a basis and uncertainty; time guidance is not an automatic human-hours rule for agents. Integrate relevant tests/checks throughout development.

Task dependencies must exist, be real and acyclic, and yield an executable sequence together with the plan's phase dependencies. Resolve ordering conflicts or phase deadlocks before approval. Logical independence does not permit concurrent execution; follow the current single-implementer and independent phase review/commit model in the [execution contract](../../harness/contracts/execution.md).

Name individual contained project-relative files, including tests and other intended changes, and distinguish existing/proposed paths. Do not target .specs, .spec-flow, or .git, directories, or wildcard scopes. Files from predecessor tasks can appear in context without expanding the current task's write permission.

## Verify contributions and retained context

Each step has an action and exactly one verification method: nonempty argv command list or specific inspection, plus expected result. Commands run from the project root, must produce meaningful output, and check the resulting task state without changing project code. Put implementation/generation/migration in actions with separate checks. Test selectors must execute relevant cases. An inspection identifies the surface, conditions, and observable evidence. Review results against approved behavior and targets; successful exit alone does not establish semantic acceptance.

The task packet retains the canonical task and its transitive dependencies but discards tasks.md prose/tables. Put all execution-critical scope, constraints, exploration boundaries, checks, and closure instructions in files, action, verification, or closure, or an approved governing source actually retained in the scoped packet. Verify that representation during drafting; do not invoke execution operations to prove document readiness. Future-work context does not authorize executing it.

For each AC, identify partial contributions and adequate final verification in canonical actions/expected results/closures. Link existing NFR definitions/targets and applicable constitution checks through actual steps without redefining acceptance. If exploration is executable under the existing contract, give it a question, boundary, expected evidence, stop condition, honest story/AC contribution, and explicit files. Otherwise return to plan. Route changed behavior or missing canonical acceptance to `$specify`; changed solution/phases to `$plan`; shared changes to their owner. Never fabricate stories or AC links merely to satisfy validation.

## Canonical tasks and table coherence

Every task appears exactly once in the task map, in canonical order, with exact id/phase/story, acceptance IDs/order, depends_on IDs/order, and closure; show None for empty dependencies. Update canonical decisions first and synchronize views in the same revision. Do not introduce fields or statuses for the reading tables.

The coverage matrix includes every spec AC once in canonical order under its actual story owner. Its contributing tasks must exactly match tasks whose acceptance contains that AC. Label partial contributions and name existing final-verification steps within those contributing tasks; explain combined checks when several steps are necessary. Reconcile methods, quality references, and delivery/final phases with spec and plan. No AC may rely only on partial tasks or a narrative promise of later verification. Keep required detail in canonical fields that survive projection.

Before presentation, approval, or handoff compare map count/order/values, criterion membership/ownership, all task/step/phase/NFR references, coverage intent, and operative context. Resolve mismatches and blockers first. Keep decision tables outside generated progress, within the decision digest. The controller checks structural contracts and nominal release AC coverage, not Markdown table coherence, semantic sufficiency, or feasibility; perform these reviews explicitly.

## Readiness, approval, and maintenance

Require current approved bases, sufficiently defined tasks across all phases, complete AC coverage/final checks, executable dependency graphs, valid file scope, usable verification, retained instructions, and resolved blockers. Progressive elaboration does not waive full-release tasks or permit undefined future work. Validate the document, then the full release with {"release":"vX.Y.Z"}; resolve every failure before approval.

Preserve completed work, historical evidence, and stable IDs for unchanged tasks/steps when refining; new work gets new IDs. Substantive postapproval edits increment revision, need approval, and require inspection/explicit adoption of affected pins. Reconcile active agents/worktree before retrying after interruption. Reuse evidence/authorization only while its exact contracts, sources, fingerprints, and scope remain applicable.

Closing a partial task does not satisfy its whole AC. Task completion requires current verification and review; phase/release closure retains independent review/commit and completion controls. Generated checkboxes are views, not proof. Approved tasks and execution authorization are distinct, though one explicit human statement may grant both scopes; reuse existing authorization within its approved scope. Neither authorizes integration, publication, or deployment by itself.

This is a Spec-Flow adaptation informed by [PMI's iteration planning](https://www.pmi.org/disciplined-agile/product-owner/practice-iteration-planning-meeting), [Bill Wake's SMART tasks](https://xp123.com/invest-in-good-stories-and-smart-tasks/), [Agile Alliance's planning](https://agilealliance.org/glossary/sprint-planning/) and [task boards](https://agilealliance.org/glossary/task-board/), [Scrum's decomposition guidance](https://scrumguides.org/scrum-guide.html#sprint-planning), and [DORA's small batches](https://dora.dev/capabilities/working-in-small-batches/) and [continuous testing](https://dora.dev/capabilities/test-automation/). It is not an official template from those sources.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>. Use validate with {"path":"..."} or {"release":"vX.Y.Z"}, digest with {"path":"..."}, gate with {"kind":"<phase>","release":"vX.Y.Z"}, and status with {}. Registry approval of the exact decision digest controls gates; a Markdown status is only a view. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Do not silently convert historical approvals or checked boxes.

Validate the resulting document. Present its concrete draft for human approval. On explicit approval call approve with {"path":"<project-relative path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}. A substantive edit after approval increments RNN and requires new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Do not approve on behalf of the user.
