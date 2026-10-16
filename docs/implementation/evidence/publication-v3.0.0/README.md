# Publication v3.0.0

The user explicitly authorized push, tag and GitHub release, preserving E7/E8 traceability and excluding user installation/update or project migration.

- preflight.json: authority, starting refs, exact package hashes and validated archive.
- protected-before.json: original installation/cache and configuration fingerprints; no private config copied.
- operations.jsonl: actual tag/push/release/notes operations and successful outcomes.
- publication-receipt.json: verified remote tag target, release, downloaded assets and installation preservation and final GitHub notes verification.
- SHA256SUMS: local evidence integrity.

The package remains byte-identical to d19d6e0. Native E7 remains tied to ef7897d and final isolated v3.0.0 installation to d19d6e0. No installation or migration operation is part of this publication.

- github-release-notes.md: final body read back from GitHub; initial-github-release-notes.md preserves the first published body.
- publication-target.json and downloaded-SHA256SUMS: immutable release target and downloaded checksum.
- final-artifact-validation.json: final package, remote publication and protected installation checks.
- reproduction/: historical scripts used for this publication. These scripts write receipts or publish and must not be rerun blindly against completed destinations.

The post-publication documentary receipt is committed and pushed separately to main. It does not move the v3.0.0 tag or alter the package. The successful final main push is confirmed by the publishing session after that receipt commit.
