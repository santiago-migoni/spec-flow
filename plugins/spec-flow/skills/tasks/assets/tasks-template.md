# Release Tasks: vX.Y.Z

```spec-flow
{
  "schema_version": 1,
  "kind": "tasks",
  "revision": "R00",
  "id": "TASKS-X.Y.Z",
  "depends_on": [
    {
      "path": ".specs/release-vX.Y.Z/plan.md",
      "digest": "0000000000000000000000000000000000000000000000000000000000000000"
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
        "src/example.py"
      ],
      "steps": [
        {
          "id": "T-001.001",
          "action": "[Implement one observable change.]",
          "verification": {
            "command": [
              "python3",
              "-m",
              "unittest"
            ],
            "expected": "[Relevant tests pass with cases executed.]"
          }
        }
      ],
      "closure": "[Observable task outcome and required evidence.]"
    }
  ]
}
```

## Task intent

[Explain sequencing and any file-scope constraints. The JSON task list above is canonical.]

## Verification notes

[Explain inspection methods where a command cannot exercise a surface. Each step still needs a specific expected result.]

## Closure

[Summarize release-level checks. Progress is generated from events; do not hand-edit checkboxes.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
