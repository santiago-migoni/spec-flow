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
      "digest": "41b1e09a052bfc9417437d418154934c75983343f7f9693faf318ab62b53b8f5"
    }
  ]
}
```

## Purpose, audience, and scope
This E7-only file placement governs the local module fixture.
## Verified current organization
The committed pre-implementation fixture tree is shown below; setup verifies these paths and stub/test hashes before registry approval. Generated controller records are omitted from this compact view.
```text
project/
├── release.py               # verified stub; sole implementation path
├── test_release.py          # verified fixed four-method suite
├── .gitignore               # verified bytecode exclusion
└── .specs/                 # verified synthetic E7 decisions
    ├── constitution.md
    ├── architecture.md
    ├── structure.md
    ├── roadmap.md
    └── release-v1.2.3/      # spec.md, plan.md, tasks.md
```
## Architecture-to-repository mapping
| Component or responsibility | Path | Current or proposed state | Entry point |
| --- | --- | --- | --- |
| Strict normalization | release.py | Verified stub; implementation planned in place | normalize_release |
| Fixed verification client | test_release.py | Verified and unchanged | unittest |
## Intended organization and placement rules
Keep the same tree; no proposed tree is needed because paths do not change.
| Path or category | Contents | Placement rule | Restrictions |
| --- | --- | --- | --- |
| release.py | Normalizer | Implement in place | Sole writable code file |
| test_release.py | Fixed checks | Retain at project root | Read-only |
| .spec-flow/ | Controller records | Managed by harness | No manual editing |
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
