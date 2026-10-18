# Changelog

## Unreleased

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
