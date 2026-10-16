# E7 existing JSON candidate

```spec-flow
{
  "schema_version": 1,
  "kind": "tasks",
  "revision": "R00",
  "id": "TASKS-1.2.3",
  "depends_on": [
    {
      "path": ".specs/release-v1.2.3/plan.md",
      "digest": "6ff2f31c6808ef32cfdecf0cf7aa3cdb54956b60a31daa68b6cd138b07db310e"
    }
  ],
  "tasks": [
    {
      "id": "T-001",
      "phase": "PH-01",
      "story": "US-001",
      "acceptance": [
        "AC-001",
        "AC-002"
      ],
      "depends_on": [],
      "files": [
        "release.py"
      ],
      "steps": [
        {
          "id": "T-001.001",
          "action": "Implement normalize_release to satisfy valid ASCII triples and exact error classes; run the fixed four-method suite without editing tests.",
          "verification": {
            "command": [
              "python3",
              "-B",
              "-m",
              "unittest",
              "-v",
              "test_release.py"
            ],
            "expected": "All four fixed tests execute and pass with exact outputs and exception types."
          }
        }
      ],
      "closure": "Final AC-001 and AC-002 behavior passes all four fixed tests; test_release.py remains unchanged."
    }
  ]
}
```

# Tasks — E7-only disposable fixture

## Purpose and approved bases
The single task realizes the approved E7 spec and plan.
## Decomposition criteria
One bounded implementation file; fixed tests are existing verification, not writable scope.
## Task map
| Task | Phase | Story | Related criteria | Dependencies | Closure condition |
| --- | --- | --- | --- | --- | --- |
| T-001 | PH-01 | US-001 | AC-001, AC-002 | None | Final behavior and four fixed tests pass |
## Sequence and dependencies
T-001 is first and only task in PH-01.
## File scope and restrictions
release.py alone is writable. test_release.py and all decision files are read-only to the implementer.
## Acceptance and quality coverage
| Criterion | Owning story | Contributing tasks | Final verification step | Quality reference |
| --- | --- | --- | --- | --- |
| AC-001 | US-001 | T-001 | T-001.001 | NFR-001 |
| AC-002 | US-001 | T-001 | T-001.001 | NFR-001 |
## Verification and evidence
Run python3 -B -m unittest -v test_release.py; retain four-case output, code fingerprint, and unchanged test hash.
## Risks, blockers, and readiness
No context omitted; strict whole-string and exception requirements survive canonical ACs and action.
## Closure and progress
Controller verify, orchestrator review, close, distinct phase review, then commit.
## Refinement, references, and approval
Synthetic E7-only decisions, with controller receipts and exact digests.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
