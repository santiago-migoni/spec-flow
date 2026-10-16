# Architecture — E7-only disposable fixture

```spec-flow
{
  "schema_version": 1,
  "kind": "architecture",
  "revision": "R00",
  "id": "ARCH-E7",
  "depends_on": [
    {
      "path": ".specs/constitution.md",
      "digest": "1cfeaf7ada550fb9f744596b7a40c4fdba85f51fa276a5ebac95250b44b8d0a3"
    }
  ]
}
```

## Purpose and approved basis
The approved E7 constitution selects a single local function and fixed test boundary.
## Responsibilities and interfaces
release.py exports normalize_release(value). It returns a canonical v-prefixed strict numeric triple or raises TypeError for nonstrings and ValueError for malformed strings. test_release.py is the immutable verification client.
## Components and interactions
Input → normalize_release → canonical string or typed exception. No storage, network, or service interface.
## Decisions and rationale
Keep implementation in one Python module and use stdlib only; this makes the contract observable through the fixed suite.
## Quality and risks
No Unicode numeric acceptance; ASCII digits only. Whole-string matching prevents whitespace and suffix acceptance.
## Verification and changes
The four fixed tests and review of actual diff establish behavior. Any changed interface needs a new approved source.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
