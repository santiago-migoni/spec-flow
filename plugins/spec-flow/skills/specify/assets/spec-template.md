# Release Spec: vX.Y.Z

```spec-flow
{
  "schema_version": 1,
  "kind": "spec",
  "revision": "R00",
  "id": "SPEC-X.Y.Z",
  "depends_on": [
    {
      "path": ".specs/roadmap.md",
      "digest": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "stories": [
    {
      "id": "US-001",
      "title": "[Story title]",
      "description": "As a [user], I need [capability] so that [benefit]."
    }
  ],
  "acceptance": [
    {
      "id": "AC-001",
      "story": "US-001",
      "description": "[Observable release behavior and criterion.]"
    }
  ]
}
```

## Release outcome

[Describe the outcome selected by the roadmap; link its entry.]

## User stories

The canonical story identities and acceptance criteria are the `stories` and `acceptance` arrays in the contract above. Keep each criterion's description there once; use this section only for narrative context that is not already in those fields.

## Release-specific nonfunctional requirements

[Measurable thresholds beyond the constitution baseline, or N/A with reason.]

## Edge cases and non-goals

[Expected edge behavior and explicit exclusions.]

## Outcome measurement

[How post-delivery results will be measured, or N/A with reason.]

## Open questions

[Resolve material questions before plan.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
