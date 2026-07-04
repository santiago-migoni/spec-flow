# Changelog

## [Unreleased]

### Added
- Tabla de control documental (Name/Code/Version/Date) en los templates de `constitution`, `spec`, `plan` y `tasks` — trazabilidad de identidad y revisión para cada artefacto. La constitution suma un `Amendments Log` append-only. La versión (`R00`, `R01`, ...) solo sube en ediciones posteriores a la primera aprobación del usuario.

## Release v0.3.0

### Changed
- Artifact root renamed from `specs/` to `.specs/` across every skill, template, and script — a clean break with no backward-compatibility shim.

### Added
- `spec-flow:clarify` — asks up to 5 targeted questions to resolve ambiguity in a feature's spec, writing answers directly into a `## Clarifications` section. Recommended before `plan`, never required.
- `spec-flow:analyze` — read-only cross-check of `spec.md`, `plan.md`, and `tasks.md` for duplication, ambiguity, coverage gaps, and constitution conflicts. Recommended before `implement`, never required, never writes a file.
