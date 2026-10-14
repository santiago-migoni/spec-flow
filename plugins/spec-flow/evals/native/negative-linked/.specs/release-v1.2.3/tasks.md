E7 evaluation task. The sole writable implementation file is release.py; test_release.py is fixed reference-equivalent verification.

```spec-flow
{
  "schema_version": 1,
  "kind": "tasks",
  "revision": "R00",
  "id": "TASKS-1.2.3",
  "depends_on": [
    {
      "path": ".specs/release-v1.2.3/plan.md",
      "digest": "0d01d0f64d997f48e97044557e1ab56fca4b372b61f60c5288a3dfe27f6ebec7"
    }
  ],
  "tasks": [
    {
      "id": "T-001",
      "phase": "PH-01",
      "story": "US-001",
      "acceptance": [
        "AC-001"
      ],
      "depends_on": [],
      "files": [
        "release.py"
      ],
      "steps": [
        {
          "id": "T-001.001",
          "action": "Implement normalize_release in release.py to satisfy the strict contract and all four existing tests.",
          "verification": {
            "command": [
              "python3",
              "-B",
              "-m",
              "unittest",
              "-v",
              "test_release.py"
            ],
            "expected": "Four tests pass."
          }
        }
      ],
      "closure": "All four behavioral tests pass with exact errors and normalized output."
    }
  ]
}
```
