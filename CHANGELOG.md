# Changelog

## Release v0.5.0

### Added
- `CLAUDE.md` — architecture guide for AI assistants working in this repo, including a per-phase model/effort rationale table.

### Changed
- `model`/`effort` tuned per phase across all nine skills, calibrated for subscription-tier usage budgets: Opus/high on judgment-heavy phases (`constitution`, `specify`, `plan`, `converge`), Opus/medium on short optional ones (`clarify`, `analyze`), Sonnet/high or medium on mechanical execution phases (`tasks`, `implement`, `finishing-branch`).
- Document control table in `constitution`, `spec`, `plan`, and `tasks` templates moved from a markdown table to YAML frontmatter — simpler for skills to edit mechanically, consistent with the frontmatter `SKILL.md` files already use.
- `spec-flow:backlog` gains priority sections (P0–P3); items are now filed under a priority instead of purely chronological order.

### Fixed
- `spec-flow:specify` now blocks writing `spec.md` while checked out on the repo's default branch, creating a feature branch first — previously nothing prevented drafting a spec directly on `main`.

## Release v0.4.0

### Added
- Tabla de control documental (Name/Code/Version/Date) en los templates de `constitution`, `spec`, `plan` y `tasks` — trazabilidad de identidad y revisión para cada artefacto. La constitution suma un `Amendments Log` append-only. La versión (`R00`, `R01`, ...) solo sube en ediciones posteriores a la primera aprobación del usuario.

## Release v0.3.0

### Changed
- Artifact root renamed from `specs/` to `.specs/` across every skill, template, and script — a clean break with no backward-compatibility shim.

### Added
- `spec-flow:clarify` — asks up to 5 targeted questions to resolve ambiguity in a feature's spec, writing answers directly into a `## Clarifications` section. Recommended before `plan`, never required.
- `spec-flow:analyze` — read-only cross-check of `spec.md`, `plan.md`, and `tasks.md` for duplication, ambiguity, coverage gaps, and constitution conflicts. Recommended before `implement`, never required, never writes a file.
