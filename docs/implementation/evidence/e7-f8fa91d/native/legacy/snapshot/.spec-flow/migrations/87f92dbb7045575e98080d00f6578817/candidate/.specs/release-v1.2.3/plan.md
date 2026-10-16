# Plan — E7-only disposable fixture

```spec-flow
{
  "schema_version": 1,
  "kind": "plan",
  "revision": "R00",
  "id": "PLAN-1.2.3",
  "depends_on": [
    {
      "path": ".specs/release-v1.2.3/spec.md",
      "digest": "57df76f5361a5de4f43873a05b09d256be92502b144343f00860970200fb1bb4"
    },
    {
      "path": ".specs/structure.md",
      "digest": "51b5ca4fe1355d23787fc5326d6343c32f2eaf92df71850889115b959abaa903"
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
Sol task review and distinct Sol phase review assess actual cases, diff, and evidence.
## Open questions and readiness for tasks
No blocking question. Task scope is one file and one fixed command.
## References, approval, and amendments
Fixture-only approval; implementation remains separately authorized.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
