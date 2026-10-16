# E7 existing JSON candidate

```spec-flow
{
  "schema_version": 1,
  "kind": "roadmap",
  "revision": "R00",
  "id": "ROADMAP-E7",
  "depends_on": [
    {
      "path": ".specs/constitution.md",
      "digest": "c8361c19642a1a5426539affda7f39d63df724dfcc0b292635dfee4880adcd64"
    },
    {
      "path": ".specs/architecture.md",
      "digest": "3dae17819e575ba2352433fbd8f70b2b558e39f4879dcb4f7aae2014256a54b0"
    },
    {
      "path": ".specs/structure.md",
      "digest": "b83a0033f71b5b9e32cd0211ae69e7aa3bc1a25959612514ccefc9fe6a2eeb05"
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

# Roadmap — E7-only disposable fixture

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
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
