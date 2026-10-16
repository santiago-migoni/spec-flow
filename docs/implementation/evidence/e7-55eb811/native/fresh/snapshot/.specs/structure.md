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
      "digest": "723047b7bc70d11a8bd39977a577956233a15c965ee653ad17c405ba9cb12ff6"
    }
  ]
}
```

## Purpose and approved bases
This structure records the verified starting tree and intended single-file change.
## Verified current tree
- release.py — existing stub; only implementation file.
- test_release.py — fixed four-method suite; read-only.
- .specs/ — controller-governed decisions.
## Proposed tree
Same paths; release.py becomes a working implementation. Generated .spec-flow records are owned by the controller.
## Placement rules
Function and helper constants stay in release.py. Tests remain byte-for-byte fixed.
## Validation and exceptions
Git diff and file hashes verify placement; no exception or path expansion is approved.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
