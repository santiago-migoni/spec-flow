# Roadmap — E7-only disposable fixture

```spec-flow
{
  "schema_version": 1,
  "kind": "roadmap",
  "revision": "R00",
  "id": "ROADMAP-E7",
  "depends_on": [
    {
      "path": ".specs/constitution.md",
      "digest": "1cfeaf7ada550fb9f744596b7a40c4fdba85f51fa276a5ebac95250b44b8d0a3"
    },
    {
      "path": ".specs/architecture.md",
      "digest": "41b1e09a052bfc9417437d418154934c75983343f7f9693faf318ab62b53b8f5"
    },
    {
      "path": ".specs/structure.md",
      "digest": "c71b1a1a748d1132cecc2cdb1ef826a1abe65e01a2cb931df68538cde6fb2d07"
    }
  ],
  "releases": [
    {
      "version": "v1.2.3",
      "objective": "Evaluate strict release normalization in disposable code.",
      "status": "planned"
    }
  ]
}
```

## Purpose, audience, and scope
One E7-only local release projection for evaluators.
## Direction and approved bases
OUT-001 is governed by the constitution, architecture, and structure. Infrastructure is N/A because this is a local pure function with no deployed environment.
## Desired outcomes and measurement
| ID | Desired outcome | Beneficiaries | Indicator | Baseline | Target | Evaluation |
| --- | --- | --- | --- | --- | --- | --- |
| OUT-001 | Strict normalization | Evaluator | Fixed unittest methods | Failing | Four pass | At technical review |
## Prioritization criteria and rationale
The sole release is first because it is the complete bounded evaluation behavior.
## Horizons and uncertainty
Now means this fixture run; no future release commitments.
## Release projections and sequence
| Version | Horizon | Expected contribution | General capabilities | Canonical status | Selection |
| --- | --- | --- | --- | --- | --- |
| v1.2.3 | Now | Evaluate strict release normalization in disposable code. | Strict normalization | planned | Selected |
## Next selected release
v1.2.3 is explicitly selected for this E7-only fixture under the user's evaluation authorization. Selection does not authorize real product delivery.
## Capacity, dependencies, and risks
Python stdlib and native host attestation are required; host failure blocks execution.
## Deferred opportunities and exclusions
No further behavior selected.
## Review, evidence, and learning
Review fixed tests and source-linked controller evidence after execution; impact is pending.
## References, approval, and amendments
Synthetic fixture decision; receipts apply only to E7.

<!-- spec-flow:generated:start -->
Spec-Flow derived record:
{"impact_status":"pending","kind":"roadmap-reference","release":"v1.2.3","run_id":"299d9b51-1a9d-4f5a-92e3-4ff20e9c58bc","schema":"spec-flow.derived-reference.v1","spec_path":".specs/release-v1.2.3/spec.md"}
<!-- spec-flow:generated:end -->
