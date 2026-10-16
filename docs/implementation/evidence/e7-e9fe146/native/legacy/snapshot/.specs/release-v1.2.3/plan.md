# E7 existing JSON candidate

```spec-flow
{
  "schema_version": 1,
  "kind": "plan",
  "revision": "R00",
  "id": "PLAN-1.2.3",
  "depends_on": [
    {
      "path": ".specs/release-v1.2.3/spec.md",
      "digest": "0b64fcf0a5e44007abe2f1d8bf98eb2125992a56ba2d0c732b09fdd6a846cc87"
    },
    {
      "path": ".specs/structure.md",
      "digest": "b83a0033f71b5b9e32cd0211ae69e7aa3bc1a25959612514ccefc9fe6a2eeb05"
    }
  ],
  "phases": [
    {
      "id": "PH-01",
      "description": "Implement and verify strict normalization in release.py.",
      "depends_on": []
    }
  ]
}
```

# Plan — E7-only disposable fixture

## Purpose, scope, and approved bases
One phase delivers US-001 under the approved E7 fixture spec and structure.
## Technical approach and implementation decisions
Use whole-string ASCII numeric matching or equivalent logic. Keep the fixed test file unchanged.
## Phases, deliverables, and dependencies
| Phase | Goal and deliverable | Dependencies | Related stories | Related criteria |
| --- | --- | --- | --- | --- |
| PH-01 | Implement and verify strict normalization in release.py. | None | US-001 | AC-001, AC-002 |
## Components, files, and change scope
| Component or path | Intended change | Phase | Restrictions or dependencies |
| --- | --- | --- | --- |
| release.py | Implement function | PH-01 | Only implementation file |
## Capacity, resources, and forecasts
One bounded native task and one independent phase review; no schedule commitment.
## Risks, assumptions, and validation
| Risk or assumption | Consequence | Response or validation | Point or phase | Expected evidence |
| --- | --- | --- | --- | --- |
| Test suite is fixed | False positives if modified | Hash comparison | PH-01 | Identical test bytes |
## Compliance and verification strategy
| Reference | Delivery or verification phase | Verification approach | Expected evidence |
| --- | --- | --- | --- |
| AC-001 | PH-01 final | Four-method suite, valid cases | Exact normalized strings |
| AC-002 | PH-01 final | Four-method suite, invalid cases | Exact exception types |
| NFR-001 → AC-001, AC-002 | PH-01 final | All four tests | Four executed tests pass |
| Constitution MUST | PH-01 | Git diff and hashes | Tests unchanged; verification nonmutating |
## Operational delivery preparation
Local Python only; no deployment.
## Review, learning, and adaptation
Orchestrator task review and distinct configured reviewer phase review assess actual cases, diff, and evidence.
## Open questions and readiness for tasks
No blocking question. Task scope is one file and one fixed command.
## References, approval, and amendments
Fixture-only approval; implementation remains separately authorized.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
