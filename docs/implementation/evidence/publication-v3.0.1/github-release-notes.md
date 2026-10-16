# Spec-Flow v3.0.1

Fix the missing listing logo declaration: both manifests now declare `logo` and `composerIcon` as `./assets/spec-flow-icon.png`. The designed image is unchanged.

- Added a packaging regression check for mirrored manifests and packaged listing/composer assets.
- Fresh isolated installation passed: 115 exact files, 128 plugin tests and 9 hook tests; PNG 1254 × 1254 verified.
- Workflow, controller, hook, profiles, gates, skills and templates are unchanged. E7/E8 reports keep their original source commits and scopes.
- User installation/configuration are unchanged; no projects were migrated.

[Release notes](https://github.com/santiago-migoni/spec-flow/blob/c8aee5704ef15433f6d404d50949a8e4cf77ac8f/docs/releases/v3.0.1.md) · [Fresh verification and original E7/E8 traceability](https://github.com/santiago-migoni/spec-flow/blob/c8aee5704ef15433f6d404d50949a8e4cf77ac8f/docs/implementation/release-v3.0.1.md)

The package declarations and assets were verified. A visible catalog refresh in an existing app session was not demonstrated. Installing/updating the user copy is a separate action.

Release commit: `c8aee5704ef15433f6d404d50949a8e4cf77ac8f`. Download `spec-flow-v3.0.1.tar.gz` and `SHA256SUMS` below; archive SHA-256: `a8690de60e579c841a507ea90a5887815cdefd7442973d9899384ddff6697e17`.
