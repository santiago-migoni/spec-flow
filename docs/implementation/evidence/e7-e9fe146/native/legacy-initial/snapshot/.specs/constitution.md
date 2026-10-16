# E7 existing JSON candidate

```spec-flow
{
  "schema_version": 1,
  "kind": "constitution",
  "revision": "R00",
  "id": "CONST-E7",
  "depends_on": []
}
```

# Constitution — E7-only disposable fixture

## Purpose and justification
Evaluate the pinned Spec-Flow package on a bounded local Python library. The baseline intentionally lacks the desired implementation; evidence is the fixed four-method suite.
## Vision and beneficiaries
The evaluator needs an exact normalization function and attributable controller evidence. This fixture has no external users.
## Objectives and success criteria
| Objective | Indicator | Baseline | Target | Evaluation point |
| --- | --- | --- | --- | --- |
| OUT-001 strict normalization | Four fixed unittest methods | Failing baseline | All pass | Before release review |
## Scope and boundaries
Only release.py may be implemented. test_release.py is fixed. Installation, delivery, and real-product approval are excluded.
## Principles
- MUST: Preserve the fixed test file and exact errors.
- MUST: Verification must leave implementation bytes unchanged.
## Responsibilities and authority
The E7 evaluator owns synthetic fixture decisions and bounded execution under the user's E7 authorization. These approvals apply solely to disposable fixtures.
## Resources, constraints, and assumptions
Use the pinned package, stdlib Python, native agents, and local linked worktrees. No external capacity or date commitments.
## Principal risks and uncertainties
| Risk or uncertainty | Possible consequence | Initial validation or response | Owner |
| --- | --- | --- | --- |
| Host attestation unavailable | Native run blocked | Validate session log before start | Evaluator |
## Delivery and learning approach
One small reviewed phase with explicit evidence and a retained branch.
## Completion and continuation criteria
Technical completion requires all tests, task closure, independent phase review, and phase commit. Impact measurement remains pending; no publication follows.
## Approval, references, and amendments
This is a synthetic E7-only decision. Controller receipts, not this prose, establish fixture authority.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
