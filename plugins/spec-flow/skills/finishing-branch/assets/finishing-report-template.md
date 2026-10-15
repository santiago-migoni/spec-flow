# Release finishing and integration: vX.Y.Z

Conversation output only. Replace placeholders with actual references/results. This report relates the original closure to later branch/publication/deployment actions; it is not another persisted controller record, editable closure document, or progress registry. Do not modify generated release records to match later actions.

## Source closure and eligibility

- Repository, release/run: [actual project, version and run_id].
- Source: [branch/worktree, current SHA and tested SHA; worktree/index state].
- Approved bases and evidence: [current registry approvals/source pins, task evidence, reviewed phase commits and receipts].
- Convergence/review: [corresponding confirmed converge assessment and actual release-review record].
- Audit checkpoint: [unique original audit SHA at source HEAD; direct parent is the last reviewed phase commit].
- Controller results on that source state: [actual gate.ready, complete.technical_complete, release_review_pending, audit_pending, and reasons; missing values remain unavailable].
- Final source checks: [required suite/checks, actual executed cases/results and conditions, evidence references and SHA tested; source remains unchanged].

Entry requires ready=true, technical_complete=true, release_review_pending=false, audit_pending=false, and actual current records/confirmed convergence. complete=true alone is insufficient. If entry fails, report the owning prerequisite and stop integration; do not label any illustrative outcome as verified. Production implementation/phase review controls remain with their existing owners.

## Prepared action and authority

- Destination: [actual repository/branch and current SHA; relevant divergence/changes; do not assume main].
- Repository requirements: [applicable allowed methods, protections, reviews/checks or merge queue; actual status].
- Selected/requested action: [retain branch / local integration / push and PR / separately authorized publication/deployment].
- Authorization: [actual declaration/reference, source/destination/action scope and any limits; or the precise missing decision on the prepared result].
- Method and candidate: [permitted fast-forward or preservation merge; candidate state/checks/review, or concrete incompatible-policy blocker].

Reuse sufficient existing authority. Opening/pushing a PR does not mean it was merged. Publication and deployment require explicit scope; one declaration may cover several actions when clear. Preserve the closed source; use a suitable separate candidate context where needed and respect worktree ownership. Recheck changed destinations before acting. Squash/rebase cannot silently inherit original receipts; a mapping note cannot replace ancestry/parent/tree validation.

## Closure-to-integration trace

| Element | Reference | Evidence |
| --- | --- | --- |
| Closed release | [Release/run and approved bases.] | [Confirmed convergence and actual release review.] |
| Reviewed implementation | [Actual phase IDs/SHAs.] | [Original receipts and current verification references.] |
| Original checkpoint | [Actual audit SHA.] | [Source closure check before integration; exact state/context.] |
| Destination before integration | [Actual branch/SHA.] | [State used for candidate preparation and applicable review/check requirements.] |
| Integrated result or pending PR | [Actual resulting SHA/method, PR URL/state, or not performed.] | [Diff/ancestry or original-commit preservation, tests/checks tied to this result; unresolved conditions.] |

Keep original and integrated SHAs distinct when they differ. Review conflict-resolution effects; list actual review/checks and any changed behavior requiring its canonical owner. Passing source tests do not prove the combined result. If an integrated destination no longer has the audit at HEAD, do not rerun closure or create another audit; the historical source checkpoint and integration have separate evidence.

## Actions and actual outcomes

| Action | Authorization | Actual result | Evidence | Remaining work |
| --- | --- | --- | --- | --- |
| Source release closure | [Existing scope/reference.] | [Verified historical checkpoint / blocked; not a new closure operation.] | [Actual review/audit records and source checks.] | [Owning prerequisite or none.] |
| Branch handling and integration | [Exact action and destination, or missing.] | [Branch retained / PR open / integration performed with checks pending or failed / integration verified / not performed.] | [Actual refs/PR/result SHA and checks, or unavailable.] | [Actual blockers/next action.] |
| Version/tag/publication | [Explicit scope or not authorized.] | [Actual package version/tag/artifact/channel outcome or not performed.] | [Identity, published reference and checks; no inferred success.] | [Authorized next step or pending decision.] |
| Deployment | [Explicit scope/environment or not authorized.] | [Actual installation/activation and operational result or not performed.] | [Actual environment, artifact/version and operation checks.] | [Authorized next step or pending decision.] |

These are conversational descriptions, not new controller statuses. Keep version/tag creation and publication distinct in the row if their outcomes differ. A planned release identifier, a successful Git command, an open PR, or pending checks do not demonstrate integration/publication/deployment success. Metadata changes must follow the repository's timing/commit rules and cannot be appended to the closed source to alter its baseline. Do not edit a forbidden changelog.

## Failures, recovery, and retained resources

[Describe actual conflicts, failed/pending checks, uncertainty and material changes. Route new behavior/solution/implementation to its canonical owner. Preserve evidence and stop affected advancement; recovery stays within authorization.]

[After interruption, identify observed local/remote refs, destination SHA, merge state, existing PR/action results and worktree state before deciding whether an operation needs retry. Do not assume a lost response means nothing happened or silently reset/revert shared work.]

[Cleanup/discard: record actual authorization and integration/PR state, needed tracked/untracked/ignored/local content, where work and original commits/evidence remain durably preserved, and what branches/worktrees were retained or removed. Respect managed-worktree mechanisms and other owners. Pending PR/checks or uncertain preservation keep the necessary resources. Discard of unintegrated work needs explicit confirmation of the exact branch/commit range.]

## Result and next action

[Summarize the verified source closure, actual chosen branch action and integration state, independently evidenced version/publication/deployment actions, unresolved checks, retained resources, and next authorized action. Distinguish results already performed from proposed or pending work.]

The original closure remains historical. This report does not persist new integration fields, update the closed review, authorize additional actions, or prove measured user/business impact. Measurement follow-up remains with its approved source and later decision reviews.
