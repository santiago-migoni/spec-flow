### Release outcome
The disposable implementation passes four substantive unittest methods equivalent to the measured Sol reference, including large components, malformed strings, and nonstrings.

```spec-flow
{
  "schema_version": 1,
  "kind": "spec",
  "revision": "R00",
  "id": "SPEC-1.2.3",
  "depends_on": [
    {
      "path": ".specs/roadmap.md",
      "digest": "e517c28f265bc86ac48cd9fb436790be43e4c21ae9272d699746c0192439def8"
    }
  ],
  "stories": [
    {
      "id": "US-001",
      "title": "Normalize release",
      "description": "A caller normalizes exact numeric release strings."
    }
  ],
  "acceptance": [
    {
      "id": "AC-001",
      "story": "US-001",
      "description": "normalize_release accepts only exact bare X.Y.Z or lowercase vX.Y.Z ASCII decimal components with no leading zeros except zero, returns vX.Y.Z; malformed strings raise ValueError and nonstrings raise TypeError."
    }
  ]
}
```
