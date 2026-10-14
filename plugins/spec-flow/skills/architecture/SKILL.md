---
name: architecture
description: "Define shared component responsibilities and interfaces from an approved constitution."
---

# Spec-Flow: architecture

<HARD-GATE>
Inspect project configuration and .specs first. If legacy NNN-feature-name artifacts exist, stop and run mandatory migrate before writing. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval for the exact constitution digest; a Markdown label is insufficient.
</HARD-GATE>

Read the constitution and current code. Write `.specs/architecture.md` using `assets/architecture-template.md`. This document owns shared components, responsibility boundaries, interfaces, data flow, and cross-release technical decisions. Decide only what planned releases need. Refer to constitution principles without copying them.

Use `kind: "architecture"` and a `depends_on` entry with the project-relative constitution path and its exact digest. Validate and request approval before dependent design work.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

Present the draft for human approval. On explicit approval, call `approve --input <json-file>` with `{"path":"<path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. The registry binds exact decision content. A substantive postapproval edit increments `RNN` and needs new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Neither a Markdown status nor old approval of different content is authority. Do not approve on the user's behalf.
