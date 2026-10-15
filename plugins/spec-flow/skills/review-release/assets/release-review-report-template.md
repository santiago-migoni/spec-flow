# Release review: vX.Y.Z

Conversation output only. Replace illustrative references with the release's actual approved sources, observations, and returned controller values. This report is richer than the persisted closure schema. Do not save it as another editable review file or copy it into generated sections/the roadmap. Its follow-up descriptions do not record actions as completed or authorize them.

## Context and eligibility

- Release/run: [actual version and run_id].
- Approved bases: [canonical document IDs/revisions, source pins, and current approval references; relevant roadmap OUT IDs and spec measurement plan].
- Evaluated implementation: [reviewed phase IDs/SHAs and current evidence references].
- Technical convergence: [corresponding converge conclusion and evidence; unresolved findings, if any].
- Controller entry: [actual gate.ready and complete.technical_complete results or unavailable; reasons; pending review/audit flags].
- Feedback context: [actual participants/roles, source and date, what was demonstrated, and feedback availability].

If entry or confirmed convergence is missing, report Not eligible and the owning next action. Do not call release-review or populate illustrative assessment rows as verified. All convergence findings, including LOW, prevent closure. The controller's technical completion alone is not the semantic convergence verdict. Pending review/audit flags describe closure work, not a technical failure.

## Accepted capabilities and feedback

Summarize actual delivered capabilities, preserving canonical US/AC ownership and referencing the current convergence assessment. Do not repeat its full audit or infer human acceptance from a demonstration, silence, or test results.

| Capability or story | Acceptance references | Convergence evidence | Feedback and provenance | Pending decision |
| --- | --- | --- | --- | --- |
| US-001: [demonstrated capability] | AC-001, AC-002, AC-003 | [Actual complete behavior and evidence reference.] | [Observed feedback, actual participant/source/context, explicit acceptance if supplied; otherwise unknown/unavailable.] | [Decision, responsible person/role and approval state, or none.] |
| US-002: [demonstrated capability] | AC-004 | [Actual integrated behavior and evidence reference.] | [Actual observation or absence of feedback.] | [Decision or none.] |

Replace these illustrative rows with actual references; they prescribe neither story count nor scope. Route approved-contract discrepancies to converge/the canonical owner. Distinguish new needs and optional suggestions from acceptance failures; missing feedback blocks only an approved obligation that requires it.

## Outcomes and measurement

Cover the indicators planned for this release, using existing roadmap/spec definitions. Keep availability of evidence separate from whether the target was reached. Use actual conditions, period, population/environment, and source; identify pilot or prior-version data and limitations on attributing results to this release.

| Outcome and indicator | Baseline and target | Observation and evidence | Measurement state | Interpretation and next step |
| --- | --- | --- | --- | --- |
| OUT-001: [existing indicator reference] | [Approved values/conditions or explicit unknowns; definition reference.] | [Actual value, period, population/environment, and durable source, or not yet measured.] | [observed / pending / unavailable] | [Target reached / not reached / inconclusive; limits; planned source, owner and date/trigger for follow-up, or missing decision.] |

- Proposed/recorded aggregate impact_status: [actual observed / pending / unavailable; explain mixed states and partial coverage].
- impact_evidence: [actual durable references; required when observed; no invented evidence].
- Measurement limitations: [what cannot be concluded, why, and whether this affects acceptance or only later outcome evaluation].

Observed can include below-target or negative results and does not establish that all outcomes were achieved or all indicators measured. Pending means a planned evaluation/window or expected data is still outstanding. Unavailable needs a reason for the current lack of usable evidence. Pending/unavailable impact alone need not prevent closure; missing acceptance evidence returns to converge.

## Delivery, limitations, and learning

- Actual delivery/exposure: [branch, artifact, integration and delivery/use facts with evidence; unknowns explicit].
- Proposed/recorded delivery_status: [actual branch_committed / branch_retained / not_integrated; basis].
- Other limitations and pending decisions: [consequences, owner and approval state; distinguish required acceptance decisions from future opportunities].

Production exposure alone does not determine branch/integration status. The operation's fixed publication/external-side-effect flags do not substitute for evidence of actual delivery. This review does not authorize integration, publication, deployment, or a version bump.

| Observation and evidence | Learning | Proposed improvement | Canonical destination | Owner and evaluation |
| --- | --- | --- | --- | --- |
| [Significant observed fact and source.] | [Supported interpretation, including uncertainty.] | [Specific proposal and actual approval state, if useful.] | [Roadmap, backlog, spec, plan, or shared decision owner.] | [Responsible person/role and how/when usefulness would be assessed if selected; unknowns explicit.] |

If there are no useful new lessons/proposals, say so and remove the illustrative row. Do not invent improvement actions or count proposals as approved tasks. Route substantive decisions through their owner; do not write their changes or another feedback/report file into the closing run.

## Persisted closure

- Operation state: [Not eligible / Ready to record / Closure blocked / Closure recorded; conversational descriptions only].
- Controller input: [actual run_id/owner and supported impact_status, impact_evidence, delivery_status only; omit unsupported narrative fields].
- Actual persisted snapshot: [returned release/run, technical_status, phase_commits, impact_status/evidence, delivery_status, publication and external_side_effects; or not recorded].
- Generated references: [actual spec generated record and roadmap reference, or not recorded].
- Audit checkpoint: [verified audit_commit_sha and actual branch state; adoption after interruption if returned; or blocked/not recorded].

The current schema does not persist this report's participants, limitations, lessons, pending decisions, per-indicator interpretation, or follow-up owner/timing as additional fields. Do not claim the full report was saved. release-review writes the supported snapshot, generated roadmap reference, event, and one final audit-only commit, then releases ownership; it does not update canonical release statuses/priorities. Do not add a second audit commit or receipt.

If interrupted, inspect durable state, actual records, HEAD/worktree, and ownership before recovery with the same input under the execution contract. Do not change the payload, manually rewrite generated tails, or add another audit to force completion. Stop on mismatches or ambiguity and report the actual blocker.

## Post-closure follow-up

[Reference the existing spec measurement plan and the next-step cells above: planned evidence source, responsible person/role, date or condition, and decisions needed. Count the measurement window from actual delivery/exposure where the plan requires it. Unknowns remain pending decisions, not invented commitments.]

[Identify where later observations will be recorded through the authorized measurement process and which subsequent roadmap/decision review should reference them. A follow-up plan is not evidence of execution or a new editable tracking system.]

Preserve the closure as the historical snapshot of what was known at that time. Later observations do not replace its impact status or evidence; never rerun release-review with different data or edit the generated snapshot. Keep the closing branch/audit checkpoint intact for finishing-branch. Subsequent measurement/decision updates use their own lifecycle/revisions/approvals and do not create another closing-branch audit commit.

## Conclusion and handoff

[Summarize demonstrated capability, actual delivery, observed/pending/unavailable results and target comparison, relevant feedback, limitations, selected or proposed learning, and next measurement/decision. Distinguish what is conversational, what was actually persisted, and what remains future follow-up.]

Report Closure recorded only after verifying the controller's actual returned records and audit SHA. Then hand integration to `$finishing-branch` under its own authorization. If entry or closure is blocked, report the owning prerequisite/action instead. Technical closure does not prove achieved outcomes or measured impact.
