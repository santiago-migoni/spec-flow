---
name: review-release
description: "Review a technically converged release's acceptance, observed impact, delivery state, and lessons before branch integration."
---

# Spec-Flow: Review Release

<HARD-GATE>
Require a release spec whose technical convergence is backed by current controller evidence and reviewed phase commits. Run the review-release gate. If tasks, verification, or convergence are incomplete, stop and direct the remaining work to the owning phase. Do not treat publication or deployment as implied by technical completion.
</HARD-GATE>

## Purpose and boundaries

Review demonstrated capabilities, actual delivery, observed outcomes, stakeholder feedback, and learning that informs subsequent decisions. Keep technical acceptance, delivery/integration, and user/business results distinct. Completed tasks and features do not establish value or measured impact.

| Representation | Purpose and location |
| --- | --- |
| Review report | Rich conversation output using [the report template](assets/release-review-report-template.md); includes feedback, interpretation, limitations, lessons, and pending decisions. |
| Persisted closure | The controller's supported snapshot in the spec's generated tail, generated roadmap reference, durable events, and single final audit commit. |
| Later follow-up | New observations in the approved measurement source, with subsequent proposals/updates through their canonical owners; not a replacement closure. |

Do not create a separate editable release-review file or copy the report into the roadmap/generated blocks. This skill does not push, merge, publish, deploy, or bump a package version.

## Entry and context

Identify release/run, approved roadmap/spec/plan/tasks and applicable decisions, current evidence, and reviewed phase commits. Read the roadmap outcomes and the spec's post-delivery measurement plan. Run the controller gate for review-release and its required live `complete` query following [shared controller operations](../../harness/contracts/operations.md) and [the execution contract](../../harness/contracts/execution.md). Completion preserves decision/execution evidence but can refresh Git metadata; strict no-file consultation cannot revalidate closure or perform the write workflow.

Require current approvals, `gate.ready=true`, `complete.technical_complete=true`, and `$converge`'s Technical convergence confirmed conclusion for the corresponding release/run, approved bases, and reviewed implementation. The controller query alone does not establish that semantic conclusion. Any outstanding convergence finding, including LOW, stops closure and returns to `$converge` and its canonical owner. Missing gate/results/evidence are not a pass. Pending release review/audit flags identify work owned here, not an acceptance defect.

Preserve the persistent owner attested against the run's pinned orchestrator profile, linked worktree, current sources/evidence, reviewed commits, and native lease requirements. Do not write report, feedback, or follow-up files into the closing worktree; unrelated changes or extra commits can invalidate closure. Resolve required decision changes through their owner and execution recovery before closing against revised bases.

## Acceptance and feedback

Summarize accepted capabilities with their actual US/AC references and the current convergence evidence; reuse that assessment rather than repeat its technical audit. Preserve canonical story ownership. Record what was demonstrated, who supplied feedback, its source/context, and any explicit acceptance or pending decision. Use available feedback without inventing attendees, agreement, or a formal approval from a demonstration. Missing feedback is reported honestly; it is a blocker only when an approved obligation requires it.

Distinguish an approved-contract discrepancy from a new need or optional opportunity. A discrepancy returns to convergence/the owning source; new needs are proposed to `$roadmap`, `$backlog`, or the appropriate decision skill without automatically changing acceptance, scope, or authorization.

## Outcomes and measurement

Reference existing roadmap outcomes and the spec's indicators, baselines, targets, method, timing, and owner. For this release's planned evaluations, report observed values, evidence/source, period, population/environment, limitations, and comparison with the approved target. Distinguish capabilities delivered, user outcomes, and organizational effects; task counts or passing tests cannot substitute for user/business observations. Label pilot, non-production, or prior-version data accurately and do not infer causality or this release's effect from a baseline alone.

Keep measurement availability separate from target attainment. Use the existing controller values:

| impact_status | Meaning in the review |
| --- | --- |
| observed | Relevant effects have usable observed evidence; durable references are required. Results may miss targets or be negative. This does not mean every indicator is measured or every outcome achieved. |
| pending | Evaluation is planned but its window has not arrived or expected data is not yet available. Identify the planned source, owner, and date/trigger. |
| unavailable | No usable evidence is available and a current limitation prevents obtaining/evaluating it. Explain the reason and any decision needed. |

Show mixed indicator states individually and justify the aggregate status, including partial coverage. Do not select observed from an unsupported claim or present one favorable indicator as overall success. Pending/unavailable impact alone need not block technical closure; missing evidence required for acceptance returns to `$converge`.

## Delivery and learning

Report branch/artifact/integration and actual delivery/exposure state from evidence. Choose only `branch_committed`, `branch_retained`, or `not_integrated` for the controller's delivery_status; production exposure alone does not establish which branch state applies. Explain any additional delivery facts in the conversation without inventing enum values or implying authorization.

Use significant qualitative/quantitative observations to explain what worked, what hindered delivery, and useful improvements. Separate evidence, interpretation, proposal, and actual approval. Select proportionate improvements with a responsible person/role and evaluation method when agreed; do not manufacture lessons/actions or turn them automatically into tasks. Route priorities to `$roadmap`, optional deferred ideas to `$backlog`, and behavior/solution/shared decisions to their owning skills. Propose future changes in the report; do not silently modify sources or add files/commits to the closing run.

## Persisted closure and recovery

When entry and required acceptance decisions are satisfied, call `release-review` using only `run_id`, `owner`, `impact_status`, optional `impact_evidence` (a list of durable references, required for observed), and optional `delivery_status`. The controller records release/run, technical_status complete, reviewed phase commits, impact status/evidence, delivery status, and its fixed `publication: false` and `external_side_effects: false`. Those flags describe this operation; they do not replace evidence of actual exposure/delivery.

Limitations, lessons, participants, pending decisions, measurement ownership/timing, and per-indicator interpretation belong to the conversational report; they are not additional payload fields or persisted narrative in the current schema. Do not claim the full report was saved. The controller writes the combined derived technical/impact snapshot, generated roadmap reference, release-review event, and one final audit-only commit, then releases ownership. It does not revise canonical roadmap release statuses/priorities. Their later changes use `$roadmap` and its approval process.

Verify returned records and `audit_commit_sha` against the actual generated records and branch checkpoint before reporting closure recorded. Do not create another generated-doc/audit commit or receipt for that audit commit. If interrupted, inspect status, durable events/records, HEAD/worktree, and ownership first. Resume only through the controller's supported recovery using the same recorded input; it may complete exact partial writes or adopt the unique matching audit commit. Changed payload, sources/code, unrelated edits, ambiguous audits, or ownership failures stop recovery; never rewrite generated tails or reset history to force a retry.

## Post-closure follow-up

Use the spec's approved measurement plan: identify each pending evaluation's existing source, owner, and date/condition. Start the observation window from actual delivery/exposure when that is what the plan requires. If the source, owner, or timing is unknown, state the missing decision and route it to its owner; do not invent a parallel tracking system. A follow-up plan does not claim a measurement or action has occurred.

Later measurements belong in the planned durable evidence source through its authorized process. Reference them in subsequent roadmap/decision reviews when appropriate, with new revisions/approvals for substantive changes. Preserve the historical closure and its original bases: never change its generated pending status to observed manually or call `release-review` again with different data. This follow-up is not another execution of release closure. Keep the closing branch/audit checkpoint intact for `$finishing-branch`; later measurement/decision updates follow their own lifecycle, not an extra commit on the pending closing branch.

## Result and handoff

Report demonstrated capabilities, actual delivery and impact status, target comparisons, feedback/limitations, lessons/proposals, and pending follow-up. Distinguish Not eligible, Ready to record, Closure blocked, and Closure recorded as conversational descriptions, not new controller statuses. On entry failure report actual reasons without claiming acceptance; on a blocked operation preserve the pending state and owning next action. Report Closure recorded only with verified controller output and the exact audit SHA, then hand branch integration to `$finishing-branch`. Technical closure with pending measurement is valid when acceptance is demonstrated; it does not prove achieved outcomes or authorize subsequent execution/integration/publication.
