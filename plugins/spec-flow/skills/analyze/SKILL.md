---
name: analyze
description: "Read-only cross-check of approved release documents, acceptance coverage, and strategic constraints."
---

# Spec-Flow: analyze

<HARD-GATE>
Require a release spec, plan, and tasks. Run gate for analyze and validate the release; report failed validation instead of treating malformed artifacts as ready.
</HARD-GATE>

## Purpose and entry

Analyze is an optional static review of one explicitly selected release's documentary preparation. Assess whether approved spec, plan, tasks, and their applicable strategic sources describe the same release with coherent scope, decisions, and sufficient planned verification. It does not demonstrate implemented behavior, confirm convergence, or assess observed impact; those belong to `$converge` and `$review-release`.

Read the release contract chain, decision prose, current registry receipts, and applicable constitution, roadmap, and shared architecture/infrastructure/structure. Use [the report template](assets/report-template.md) for a conversation-only report. Identify date, release, inspected paths/revisions/decision digests, actual versus pinned bases, approval evidence, scope, and unavailable material. Record the actual Git reference/working state when relevant using read-only queries; do not invent a clean committed snapshot. If sources change during review, identify the stale/mixed base and repeat affected checks before a readiness conclusion.

Run `validate` with {"release":"vX.Y.Z"} and `gate` with {"kind":"analyze","release":"vX.Y.Z"}. The phase gate validates the full release and requires current approval of spec, plan, tasks, and their dependency closure. Keep validation results, approval/gate results, and semantic findings distinct. A failed query, missing document/approval, malformed contract, stale pin, uninitialized project, or required legacy migration prevents a full eligible review and a recommendation to implement. Preserve errors and missing/unavailable values; further inspection is diagnostic only, with its limits explicit. Do not bypass a failed control by validating a different scope or substituting a Markdown status.

## Read-only queries

Do not write any file or alter approvals. Do not save reports/patches, initialize, migrate (including preview), repair state, refresh evidence, generate progress, or invoke execution operations. Inspect proposed task checks without running them. Do not create input JSON files, scratch files, or Python caches to perform this review. Read-only findings and exact proposed edits stay in conversation.

Before invoking `spec-flow.py`, read [strict consultation](../../harness/contracts/operations.md#strict-consultation) for the no-file CLI/input and Git-read mechanics. Only use `status` with {}, `validate` with the release or a supported path, `digest` with a supported path, and the analyze phase `gate` above. Use `GIT_OPTIONAL_LOCKS=0 python3 -B` and existing inputs or `/dev/stdin`; preserve query errors without repair. Unadopted/legacy projects remain diagnostic-only; setup and migration belong to a separate authorized owner workflow. Never convert historical approvals or checked boxes into authority.

## Semantic review

Review available sources from business, development, and testing perspectives, using concrete normal/edge/error scenarios where useful without inventing participants or forcing a meeting. Check:

- **Strategy and scope:** selected roadmap release/outcomes, constitution MUSTs, exclusions, and bounded story value; detect unjustified scope or omitted obligations.
- **Stories and acceptance:** clarity, feasibility, observable conditions, known US/AC/NFR references, correct story ownership, and unresolved material questions.
- **Shared design:** compatible component/contracts/data, operational/recovery constraints, and repository mappings; use only applicable documents and distinguish N/A from an omitted dependency.
- **Plan and phases:** solution/deliverables, phase membership/dependency order, risk/capacity assumptions, and operational/transition preparation consistent with approved scope.
- **Tasks and checks:** explicit file scope, usable actions/closures, task dependencies, concrete expected verification, and sufficient planned checks rather than nominal ID coverage.
- **Quality and transition:** applicable performance/security/availability/usability, error/compatibility/data-transition and delivery obligations reflected in canonical acceptance and planned work.
- **Canonical records and views:** story/outcome/AC examples and quality tables, phase tables, task maps and coverage matrices match actual IDs/order/ownership/membership and definitions. Explain contradictions against both sources; legitimate references or context are not automatically duplication. Distinguish current decisions, proposals, and explicitly superseded clarification/decision history.
- **Retained execution context:** necessary scope/constraints/checks/closure instructions exist in canonical task fields or approved governing sources actually retained by packet projection. tasks.md prose/tables alone do not reach the implementer. Inspect definitions/projection guidance without invoking prepare or executing tasks.

The controller checks structural contracts, dependency digests/graphs, references, ownership, and nominal full-release AC coverage; it does not assess Markdown table coherence or semantic sufficiency. Do not require speculative future releases or extra documents merely to complete this review. Progressive detail does not waive the current full-release tasks/coverage requirement.

## Planned coverage

Include every AC once in canonical spec order under its real story owner. List all contributing tasks exactly as declared in their acceptance references, their actual phases, and existing final-verification step IDs/methods/expected results. Keep partial contributions explicit and assess whether their combined checks cover every required condition, including referenced NFR targets. Reference targets at their defining source instead of creating another editable acceptance definition.

A concrete check can still be irrelevant: file existence does not establish a specified latency under load. An AC supported only by partial tasks or a narrative promise of later checking lacks sufficient planned final verification. Classify the plan as sufficient, partial, contradictory, or not evaluable with evidence and finding references; these are conversation descriptions, not runtime statuses. Never invent steps, test results, IDs, owners, or mappings. Do not equate a covered ID or a planned sufficient check with demonstrated acceptance. If reporting percentages, give the actual denominator/scope and identify nominal versus assessed coverage; omit unsupported totals when inputs are incomplete.

## Findings and canonical routing

Report actual duplication, ambiguity, inconsistency, stale dependencies, uncovered obligations, insufficient verification, constitution MUST conflicts, and plan/strategy mismatch. For each finding include stable report-local ID, type, justified severity, exact locations/US/AC/PH/T/step references where applicable, observed evidence, consequence, and a concrete proposed correction with owning skill. Separate unresolved questions without enough evidence and optional opportunities; do not invent findings to fill a quota.

| Severity | Guideline |
| --- | --- |
| CRITICAL | Constitution MUST violation or fundamental contradiction preventing a recommendation to implement. |
| HIGH | Material scope, acceptance, design, or verification defect with significant consequences for affected work. |
| MEDIUM | Relevant inconsistency or ambiguity with localized consequences. |
| LOW | Minor clarity/consistency defect with limited consequences. |

A CRITICAL finding blocks recommending implementation. Failed validation/gates block independently of finding severity. Explain any other finding that prevents adequate preparation and the affected scope; do not impose converge's zero-findings condition as a new runtime gate. Zero findings is valid within the actual review scope.

Route principles to `$constitution`, shared decisions to `$design`, priorities/release boundaries to `$roadmap`, behavior/acceptance to `$specify` (or `$clarify` for its eligible approved-base clarification), solution/phases to `$plan`, and actions/checks/retained task instructions to `$tasks`. Deferred optional proposals may be suggested for `$backlog`; approved obligations require an approved scope change before deferral. Do not create another requirements, task, or finding registry.

Offer exact edits for the owner skill to apply after user authorization. Accepting exact proposed wording can supply approval of that content without redundant confirmation; broader answers do not approve unseen additions. Analyze remains read-only: application, validation, approval recording, revision changes, and explicit downstream adoption occur in a separate owner workflow under its gates. If execution is active, identify required reconciliation/recovery without performing it or rewriting historical evidence.

## Conclusion

Report full versus diagnostic/limited scope, actual controller outcomes, assessed coverage, findings, remaining questions/limitations, and the next authorized destination. No findings means none detected in the reviewed scope, not exhaustive correctness, implementation, or observed impact. Missing material prevents an unqualified clean conclusion. Current approvals bind exact decision digests; generated Markdown views and historical receipts for different content are not authority.

Analyze does not grant execution authorization or replace the runtime gate. Keep any existing execution authority separate from documentary readiness and do not start implementation from this review.

This adaptation uses [PMI's agile documentation guidance](https://www.pmi.org/disciplined-agile/agile/documentation), [IIBA's traceability guidance](https://www.iiba.org/knowledgehub/the-business-analysis-standard/4-implementing-business-analysis/4-4-understanding-requirements-and-designs/), [Agile Alliance's Three Amigos](https://agilealliance.org/glossary/three-amigos/), [Cucumber's Example Mapping](https://cucumber.io/docs/bdd/example-mapping/), and [ISTQB's static review guidance, chapter 3](https://istqb.org/wp-content/uploads/2024/11/ISTQB_CTFL_Syllabus_v4.0.1.pdf); it is not an official template from those sources.
