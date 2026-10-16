# Publication v3.0.0

The user explicitly authorized push, tag and GitHub release, preserving E7/E8 traceability and excluding user installation/update or project migration.

- preflight.json: authority, starting refs, exact package hashes and validated archive.
- protected-before.json: original installation/cache and configuration fingerprints; no private config copied.
- operations.jsonl: actual tag/push/release operations and outcomes, once executed.
- publication-receipt.json: verified remote tag target, release, downloaded assets and installation preservation, once available.
- SHA256SUMS: local evidence integrity.

The package remains byte-identical to d19d6e0. Native E7 remains tied to ef7897d and final isolated v3.0.0 installation to d19d6e0. No installation or migration operation is part of this publication.
