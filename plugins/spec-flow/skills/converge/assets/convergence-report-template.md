# Convergence assessment: vX.Y.Z

Conversation output only. Replace illustrative references with actual approved sources and observed evidence. Do not save this report as another editable artifact, acceptance registry, or gap list. A new report does not require rerunning valid checks.

## Context and eligibility

- Release and execution: [vX.Y.Z; run_id].
- Approved bases: [canonical paths, document IDs/revisions, source pins, and current registry approval references].
- Evaluated state: [current SHA; each reviewed phase ID and commit SHA; relevant environment/configuration/data/inspection conditions].
- Controller `gate.ready`: [actual result or unavailable; reasons].
- Controller `complete.technical_complete`: [actual result or unavailable; reasons].
- Later closure: [actual `release_review_pending` and `audit_pending`, or unavailable; these flags alone do not block convergence assessment].

Require both entry results to be true. If either fails or is unavailable, report Not eligible with the owning prerequisite and next action. Mark acceptance/integrated assessment Not assessed and omit their illustrative rows; do not fabricate coverage or assess implementation from a failed gate. Controller completion is an entry condition, not the semantic convergence verdict.

## Acceptance coverage

Include every AC exactly once in canonical spec order under its actual story. Reference real contributing tasks/phases and existing final-verification step IDs. This is an evidence view of canonical definitions, not a copy of their requirements or a progress registry. Replace these rows with the release's full AC list; do not infer a fixed number of stories, tasks, or checks.

| AC | Owning story | Contributing tasks and phases | Final verification | Current evidence | Result |
| --- | --- | --- | --- | --- | --- |
| AC-001 | US-001 | T-001: partial; T-002: final, PH-01 | T-002.001 | [Receipt/output/commit demonstrating the complete approved behavior.] | [Result] |
| AC-002 | US-001 | T-002, PH-01 | T-002.002 | [Observed invalid-input/error behavior against the approved expectation.] | [Result] |
| AC-003 | US-001 | T-002, PH-01 | T-002.003; NFR-001 | [Approved target/conditions/method reference and observed measurement/comparison.] | [Result] |
| AC-004 | US-002 | T-003, PH-02 | T-003.001 | [Integrated behavior and relevant regression evidence.] | [Result] |

Results: Satisfied / Gap / Not verifiable. A partial contribution alone cannot satisfy an AC; a passing check must demonstrate its full obligation under the approved conditions. Identify absent/inadequate final verification explicitly rather than inventing a step. Missing or insufficient evidence requires a finding. N/A cannot discard an approved AC.

## Integrated assessment

Select aspects relevant to this release's approved scope, quality/completion conditions, and actual shared-design dependencies. Do not require every shared document or every listed operational category. Include applicable obligations beyond ACs without creating new acceptance IDs or duplicating their definitions.

| Aspect | Approved basis | Evidence and examined scope | Result |
| --- | --- | --- | --- |
| Integrated journeys, interfaces, compatibility, and errors | [Relevant ACs and adopted decisions.] | [Observed end-to-end/interface behavior and conditions.] | [Result] |
| Relevant regressions | [Behavior/constraints to preserve and approved verification strategy.] | [Checks, results, and coverage limits.] | [Result] |
| Shared decisions and completion/quality obligations | [Applicable constitution, architecture, infrastructure, structure, spec, or plan references.] | [Observed conformance to responsibilities, placement, operating constraints, and required thresholds.] | [Result] |
| Technical delivery preparation | [Approved documentation, configuration, packaging, migration, observability, or recovery obligations that apply.] | [Evidence for applicable obligations; approved-scope reason for any N/A.] | [Result] |

Results: Satisfied / Gap / Not verifiable / N/A with reason. Split rows when their obligations have different results or applicability. N/A cannot waive an approved applicable obligation. Relevant unmet obligations or insufficient evidence require findings.

## Findings

Include actual approved-contract discrepancies, including insufficient evidence. Type: missing / partial / contradictory / unrequested. Unrequested refers to implemented behavior outside approved boundaries, not an optional suggestion. Severity: CRITICAL / HIGH / MEDIUM / LOW, justified by consequence; a constitution MUST violation is CRITICAL. Any remaining finding prevents a clean outcome.

| ID | Type and severity | Canonical source | Expected versus observed | Evidence and impact | Proposed change and destination |
| --- | --- | --- | --- | --- | --- |
| F-01 | [Type; severity and rationale.] | [Actual AC, plan/shared decision, or constitution obligation reference.] | [Approved expectation and precise observed discrepancy or missing demonstration.] | [Receipt/output/file/commit references and consequence.] | [Exact proposed canonical change and owning skill.] |

If none remain, replace the illustrative row with an explicit zero-findings statement. For implementation/verification gaps, present the proposed canonical tasks change with ID, phase, story/ACs, dependencies, files, steps/checks, and closure. Do not implement it here or defer an approved obligation to backlog without an approved scope change.

## Limitations and opportunities

[State evidence/environment/coverage limits and their effect on the conclusion. Link any limitation that prevents demonstrating an approved obligation to its Not verifiable result and finding. Other limits need not invent a failure.]

[Optional opportunities, when useful: brief proposals outside required acceptance, with their appropriate roadmap/backlog/decision owner. These are not findings, approved scope, automatic tasks, or another editable work list. Omit if none.]

## Outcome and handoff

- Assessment conclusion: [Not eligible / Technical convergence not confirmed / Technical convergence confirmed]. This is conversational, not a new controller field or persisted status.
- Basis: [entry results, complete AC/applicable-obligation coverage, evidence sufficiency, finding count/severities, and material limitations].
- Next action: [owning prerequisite, exact proposed canonical change awaiting approval, or `$review-release`].

Confirm technical convergence only when entry passed, every AC and applicable approved obligation is demonstrated, and zero findings remain. Otherwise preserve the actual reasons and pending work. Optional suggestions alone do not prevent confirmation.

- Confirmed: leave approved content and `tasks.md` unchanged. Report the actual live `complete.technical_complete` result, release/run, reviewed phase commits, and current evidence. Completion can refresh Git metadata and is excluded from strict no-file consultation; a historical record is not a live result. Continue to `$review-release`; that skill records the combined derived outcome. Do not mark the spec Converged, write a generated closure note, or call `release-review` from converge.
- Implementation/verification gap: show the exact canonical tasks change for approval, then hand off through `$tasks` and `$implement` as applicable. Reconcile execution state, agents/worktree, approvals/source pins, and authorization before execution; changed sources use the authorized recovery/new-run path, not an assumed reopening of committed phases.
- Decision gap: return to `$specify`, `$plan`, or the owning strategy/shared-design skill. Review only dependent decisions that adopt the changed base. An exact recommendation accepted verbatim can approve that change; broader wording needs review.

Subsequent passes recheck entry and the updated release, reuse valid unaffected evidence, and examine affected behavior/interfaces/regressions. Technical convergence does not prove measured impact or authorize integration, publication, deployment, or a version bump.
