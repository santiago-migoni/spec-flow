A single phase implements the exact normalization contract in release.py and runs the four existing tests.

```spec-flow
{
  "schema_version": 1,
  "kind": "plan",
  "revision": "R00",
  "id": "PLAN-1.2.3",
  "depends_on": [
    {
      "path": ".specs/release-v1.2.3/spec.md",
      "digest": "04efe4ab0763b9fc2c25f64db9de84aeeda02ebac2428fc0a442eb090dd71878"
    }
  ],
  "phases": [
    {
      "id": "PH-01",
      "description": "Implement and verify strict normalization.",
      "depends_on": []
    }
  ]
}
```
