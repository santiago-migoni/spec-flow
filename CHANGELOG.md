# Changelog

## Unreleased

### Added

- Spec-Flow as a Claude Code plugin: a strategic flow (constitution, design, roadmap), an operational release flow (spec, plan, tasks, implement, review-release, finishing-branch), and a backlog for deferred ideas.
- Document approval controller: `initialize`, `digest`, `validate`, `approve`, `gate`, `hook-check`, and migration operations. Approvals are recorded per exact content and checked against exact-digest dependencies.
- `PreToolUse` hook that checks `Edit`, `MultiEdit`, and `Write` calls against document approvals and protects `.spec-flow/`.
- Marketplace and plugin manifests for Claude Code.
