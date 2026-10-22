# Changelog

## Unreleased

### Added

- `grilling` skill: an optional, conversation-only side channel that grills an idea, plan, or decision one question at a time, or brainstorms options first. It writes no file and gates nothing.

## Release v0.4.0

Release date: 2026-10-22.

### Changed

- `approve` now sets `status: approved` in the document's YAML header before recording the digest. The status is outside the digest, so a draft's digest is the one that stays recorded and pins taken from it remain valid. Documents without a YAML header are approved as before; `validate` warns when the status is `approved` but no current receipt exists. The document templates start with `status: draft` and no longer carry approval state in the prose.

## Release v0.3.0

Release date: 2026-10-21.

### Removed

- The `clarify` and `analyze` skills and their templates, with their `gate` phases in the controller and their entries in the README and `using-spec-flow` routing. Spec ambiguities are now resolved in `specify`.

### Changed

- Tasks guidance caps a release at about 10 tasks (frontmatter size) and says to split the release past that; the closure text now appears only in the array and the task map.
- The "never write on the default branch" rule moved from the spec template into the `specify` skill.
- Constitution, architecture, infrastructure, structure, roadmap, spec, plan, tasks, and backlog templates are rewritten as table-first documents with a deletable "Authoring notes" block, one-sentence section guides, and Mermaid diagrams; the roadmap template's example releases start at `v1.0.0`.
- A document that still contains the "Authoring notes" block is now rejected as containing a placeholder.

## Release v0.2.0

Release date: 2026-10-18.

### Fixed

- A missing prerequisite document now reports `dependency_not_approved` with "missing; write and approve it first" instead of `contract_invalid: cannot read document`, in both the hook and the gate.
- Text added after a document's generated progress block now names the fix ("move any text added after it above the block") instead of only stating the block shape.

## Release v0.1.0

Release date: 2026-10-17.

### Added

- Spec-Flow as a Claude Code plugin: a strategic flow (constitution, design, roadmap), an operational release flow (spec, plan, tasks, implement, review-release, finishing-branch), and a backlog for deferred ideas.
- Document approval controller: `initialize`, `digest`, `validate`, `approve`, `gate`, `hook-check`, and migration operations. Approvals are recorded per exact content and checked against exact-digest dependencies.
- `PreToolUse` hook that checks `Edit`, `MultiEdit`, and `Write` calls against document approvals and protects `.spec-flow/`.
- Marketplace and plugin manifests for Claude Code.
