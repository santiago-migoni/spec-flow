# Spec: Codex Plugin Migration

<!-- Every claim in this document must be measurable or falsifiable — avoid vague adjectives without a concrete threshold or test. -->

| Name                  | Code     | Version | Date       | Status |
| --------------------- | -------- | ------- | ---------- | ------ |
| codex-plugin-migration | SPEC-006 | R02     | 2026-09-12 | Converged |

## Summary

Convert spec-flow from a Claude Code plugin into an installable Codex plugin while preserving its seven-phase workflow, optional skills, artifact formats, and approval gates.

## Success Metrics

- Skill discovery: all 11 skills are listed by Codex after installing the repository plugin, and each can be selected or invoked using the name Codex exposes.
- Workflow parity: the seven gated phases and two quality side-channel skills complete their documented flows in Codex without Claude-specific commands.
- Approval protection: with plugin hooks trusted, blocked and approved gate scenarios behave as specified; without hook trust, each skill's hard gate still prevents downstream artifact writes.
- Host-specific residue: no active manifest, install instruction, or runtime path requires Claude Code.
- GitHub marketplace install: adding `santiago-migoni/spec-flow` through Codex resolves the version-controlled marketplace and installs the plugin from the repository's GitHub-backed package path.

## User Stories

### US1 — Installable Codex plugin (P1)

As a Codex user, I can install spec-flow from its repository and discover its skills without Claude Code metadata or services.

**Acceptance Scenarios**:

- **Given** the repository is installed as a Codex plugin, **When** Codex loads it, **Then** it discovers all 11 skill directories under `skills/` and exposes them for selection or direct invocation.
- **Given** the plugin has no MCP server or custom UI, **When** Codex loads the package, **Then** the skills and their bundled templates, references, and scripts remain available.

### US2 — Codex-native skill workflow (P1)

As a user running spec-flow in Codex, I can follow the same phase chain and side-channel workflows with host-native skill activation and guidance.

**Acceptance Scenarios**:

- **Given** I request the spec-flow bootstrap workflow in Codex, **When** its skill activates, **Then** it presents the seven phases in order, identifies `clarify` and `analyze` as optional, and describes the `.specs/` artifact layout.
- **Given** I request a phase skill directly or by matching its description, **When** Codex loads it, **Then** its `SKILL.md`, referenced templates, and scripts are available and the skill follows its documented process.
- **Given** I read the repository usage and maintainer instructions, **When** I follow their install and invocation steps, **Then** they use Codex-supported paths and commands and do not require Claude Code.

### US3 — Approval gates in Codex (P1)

As a user, I need the prior-artifact and explicit-approval rules to remain effective when Codex runs a phase skill.

**Acceptance Scenarios**:

- **Given** a required prior artifact is absent or has `Status: Draft`, **When** I request its downstream phase, **Then** the phase stops before writing the next artifact and explains the missing artifact or approval.
- **Given** the prior artifact has an allowed approved status, **When** I request the downstream phase, **Then** the phase may proceed subject to its other hard-gate requirements.
- **Given** the plugin hooks are trusted and Codex attempts a blocked write through a supported local write tool, **When** the approval hook evaluates it, **Then** it denies the write and returns a reason identifying the required approval.
- **Given** plugin hooks have not been trusted, **When** I invoke a downstream phase against a missing or Draft artifact, **Then** the skill's own hard gate still stops before writing and the install guidance explains that hook enforcement requires trust.

### US4 — Codex repository guidance (P2)

As a maintainer, I can update, validate, and release the Codex plugin using repository instructions that match its actual files.

**Acceptance Scenarios**:

- **Given** a maintainer reads the repository agent guide, **When** they follow its architecture, skill, script, manifest, and release instructions, **Then** every named path exists and the described plugin format matches Codex.
- **Given** a maintainer follows `README.md`, **When** they install and invoke spec-flow, **Then** the instructions target Codex and do not point to `.claude-plugin` or Claude Code commands.

### US5 — Install from the GitHub-hosted marketplace (P2)

As a Codex user, I can add this repository's marketplace from GitHub and install spec-flow from a GitHub-backed plugin source.

**Acceptance Scenarios**:

- **Given** the GitHub repository is reachable from my Codex environment, **When** I add `santiago-migoni/spec-flow` as a marketplace, **Then** Codex lists the `spec-flow` entry from the marketplace on the `main` ref.
- **Given** I install `spec-flow` from that marketplace, **When** Codex resolves its GitHub-backed `git-subdir` source, **Then** it loads `./plugins/spec-flow` at ref `main`, including the portable manifest and all 11 skills.
- **Given** the marketplace and plugin source are declared in GitHub, **When** I follow the documented setup commands, **Then** I do not need a local repository checkout or manual edits to my personal marketplace file.

## Non-Functional Requirements

- **MUST**: The package uses the portable Agent Plugins root `plugin.json` format, with OpenAI-specific hook configuration in `extensions.com.openai` when required.
- **MUST**: Every skill uses Codex-supported `SKILL.md` metadata (`name` and `description`); Claude-specific runtime metadata must not be required for skill discovery or execution.
- **MUST**: The seven-phase chain, side-channel distinction, `.specs/` artifacts, and approval-state semantics remain unchanged.
- **MUST**: The repository contains a valid, version-controlled Codex marketplace entry whose GitHub `git-subdir` source points to `./plugins/spec-flow` at ref `main`, and whose installation instructions use the GitHub-hosted marketplace.
- **MUST**: `README.md`, `AGENTS.md`, and `.specs/constitution.md` describe Codex as the supported host and match the migrated package, skill, hook, marketplace, and release paths.
- **MUST**: The plugin remains skills-only: no MCP server, custom UI, runtime network dependency, or external runtime service is introduced. GitHub access is used only to retrieve and update the marketplace and plugin package during installation.
- **SHOULD**: The approval hook uses `PLUGIN_ROOT` and Codex's hook input/output schema, and its supported tool paths and trust requirement are documented.

## Edge Cases

- A user invokes a downstream phase when its prior artifact is missing or `Draft`.
- The approval hook has not been trusted or is unavailable; the skill-level hard gate still applies.
- A Codex hook sees an unsupported tool path; the workflow instructions still block phase progression, and documentation does not claim the hook covers that path.
- A Codex plugin is installed in an environment where its hook script cannot execute; skills remain discoverable and the user receives clear guidance about the missing enforcement hook.

## Assumptions & Dependencies

- Codex's portable Agent Plugins package format is the target; Codex is the required runtime to verify. Publishing to the public plugin directory is not required for this feature.
- The marketplace is versioned in this GitHub repository; Codex can reach the repository (publicly or with the user's existing GitHub access), and the tracked source ref is `main`. This feature does not change the user's personal marketplace configuration directly.
- The current skill workflows and templates are the source of truth for behavior; host-specific packaging, metadata, hooks, installation, and invocation instructions are what change.
- Codex supports bundled skills and lifecycle hooks, but plugin hooks require user trust and must be validated against Codex's current event schema.

## Explicit Non-Goals

- No changes to the meaning, ordering, or approval policy of the seven phases.
- No Claude Code compatibility package or dual-host maintenance.
- No MCP server, app integration, custom UI, or public-directory submission.
- No redesign of the consuming project's `.specs/` artifact formats.

## Open Questions

<!-- Empty section is a valid, finished state — don't invent a question to fill it. -->
