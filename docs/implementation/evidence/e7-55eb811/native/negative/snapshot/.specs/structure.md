# Structure — E7-only disposable fixture

```spec-flow
{
  "schema_version": 1,
  "kind": "structure",
  "revision": "R00",
  "id": "STRUCT-E7",
  "depends_on": [
    {
      "path": ".specs/constitution.md",
      "digest": "1cfeaf7ada550fb9f744596b7a40c4fdba85f51fa276a5ebac95250b44b8d0a3"
    },
    {
      "path": ".specs/architecture.md",
      "digest": "68fadf86f5eac936fabbb35dbd05b51e9ab969693cd970736bd598848d8174c8"
    }
  ]
}
```

## Purpose, audience, and scope
This E7-only file placement governs the local module fixture.
## Verified current organization
The verified starting tree has release.py (stub), test_release.py (fixed four-method suite), .specs/ (decisions), and .spec-flow/ (controller records after adoption).
## Architecture-to-repository mapping
The architecture's normalize_release contract maps to release.py; the immutable client and test evidence map to test_release.py.
## Intended organization and placement rules
Keep the same tree. Edit release.py only for implementation; controller owns .spec-flow and generated progress.
## Naming conventions and public interfaces
Export normalize_release exactly from release.py; no package rename or added entry point.
## Dependencies and module boundaries
Only Python stdlib may be imported. The test imports release; release must not import test_release.
## Tests, configuration, documentation, and resources
The fixed test_release.py is read-only. There is no runtime config or resource required for this pure function.
## Generated files, third parties, and distribution
The controller manages generated .spec-flow records; Python bytecode is ignored. No third-party package or distribution target.
## Decisions, risks, and pending structural changes
The permitted implementation scope is release.py. A changed path requires an approved tasks/structure revision; none is pending.
## References and amendment history
Synthetic E7-only R00 decision; initial tree inspected before approval.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
