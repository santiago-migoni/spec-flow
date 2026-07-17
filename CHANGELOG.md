# Changelog

## Release v0.7.0

### Added
- `spec-flow:clarify` gains `assets/clarifications-template.md` and `spec-flow:analyze` gains `assets/report-template.md` — both side-channel skills now use a templated output format, matching the convention already used by the seven gated phases.

### Changed
- Redesigned the `constitution`, `spec`, `plan`, and `tasks` templates to resolve embedded ambiguities: user-story/phase blocks are now marked as explicitly repeatable (previously hardcoded to exactly two stories), the constitution's `Tech Stack` fields use one consistent `"N/A"` convention instead of mixing in `NEEDS CLARIFICATION`, `plan.md`'s File Structure fence separates the fill-in instruction from the literal example tree, and `spec.md`'s `status` field documents its two valid values (`Draft`, `Converged`) inline as a YAML comment.
- `constitution-template.md` gains `Security`, `Operational Principles`, `Observability`, `Performance`, and `Dependency Policy` sections, and tags every bullet in a principle section with an RFC 2119 keyword (`MUST`/`SHOULD`/`MAY`) — `MUST` is now a literal, greppable marker instead of an implicit concept that `analyze` and `converge` referenced without any way to identify it in the document. `constitution/SKILL.md` documents the convention in a new "Principle Keywords" section.
- `spec-template.md` gains `Success Metrics`, `Non-Functional Requirements`, and `Assumptions & Dependencies` sections, plus a document-wide guardrail comment against unmeasurable language (ties directly into `analyze`'s existing Ambiguity check). Deliberately does not add a separately-numbered `Functional Requirements` list — `analyze`/`converge` already treat `USn/ACn` as the atomic requirement ID, and a second numbering scheme would fragment that instead of resolving ambiguity. `specify/SKILL.md`'s clarifying-question focus and quality check updated to match.
- `plan-template.md`'s `Constitution Check` expanded from 3 to 8 checks — it only covered `Tech Stack`/`Code Principles`/`Constraints` and had gone stale against constitution's new `Security`/`Operational Principles`/`Observability`/`Performance`/`Dependency Policy` sections, so a plan could violate a new `MUST` with nothing catching it. Also adds `NFR Compliance` (checks the plan against `spec.md`'s Non-Functional Requirements) and an optional Mermaid diagram in `Architecture` for multi-component designs. `plan/SKILL.md`'s process and quality check updated to match.
- `tasks-template.md` gains a `[TEST]` task tag (writes/updates a test for a sibling task, combinable with `[P]`) and two new `Verification` items — Non-Functional Requirements met, and no relevant constitution `MUST` violated — closing the loop with the NFR and principle-keyword work added to `spec.md`/`constitution.md`/`plan.md` earlier. `tasks/SKILL.md`'s Task Format and quality check updated to match.
- `spec-flow:analyze`'s inventory now includes `spec.md`'s Non-Functional Requirements and Success Metrics, `MUST`s across every constitution principle section (not just `Code Principles`), and a structural check of `tasks.md` (every user-story phase has a `[TEST]` task, the new `VERIFY` lines are present). No new finding category was added — these gaps still classify as existing `Ambiguity`/`Coverage gap`/`Constitution conflict` types. `assets/report-template.md`'s Coverage Summary now shows an NFR row alongside the `USn/ACn` row.
- `spec-flow:clarify`'s five ambiguity-scan dimensions are now mapped 1:1 to real `spec.md` sections (`User Stories`/`Edge Cases`, `Success Metrics`, `Non-Functional Requirements`, `Assumptions & Dependencies`, `Explicit Non-Goals`/terminology) instead of generic category names that didn't point at where an answer gets written. Dropped `data model / entities` as its own dimension — `spec.md` has no section that owns data modeling (that's `plan.md`'s job); entity ambiguity now surfaces through `User Stories` instead of a dimension with nowhere to land.

## Release v0.6.0

### Added
- `spec-flow:finishing-branch` derives the CHANGELOG heading (`Added`/`Fixed`/`Changed`) and a recommended SemVer bump (`MAJOR`/`MINOR`/`PATCH`/none) from the branch's Conventional Commits history — `feat` → MINOR, `fix`/`refactor` → PATCH, `!`/`BREAKING CHANGE:` → MAJOR. Its own housekeeping commit now follows the Conventional Commits format (`docs(NNN-feature-name): ...`).
- `spec-flow:using-spec-flow` gains a Markdown Style section — markdownlint-derived rules (heading increments, blank-line spacing around headings/lists/fences, fenced-code language, no bare URLs, single trailing newline) that every phase follows when writing `.specs/` artifacts.

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
