---
name: constitution
description: "Create or revise project purpose, users, outcomes, principles, and boundaries."
---

# Spec-Flow: constitution

<HARD-GATE>
Inspect project configuration and .specs first. If legacy NNN-feature-name artifacts exist, stop and run mandatory migrate before writing. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. This first decision document must be approved in the registry before dependent work.
</HARD-GATE>

Read the repository, README, AGENTS.md, and root configuration for current facts. Ask the user about purpose, users, outcomes, principles, and boundaries whenever human direction is unknown; these product choices cannot be inferred from code. Write `.specs/constitution.md` using `assets/constitution-template.md`. It owns product purpose, goals, and principles. Component design belongs in architecture, paths in structure, environments in infrastructure, and priorities in roadmap.

Use `kind: "constitution"` and `depends_on: []`. Make MUST statements testable and leave unknowns as questions. An approved amendment requires a new revision and approval; downstream dependency digests may become stale.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

Present the draft for human approval. On explicit approval, call `approve --input <json-file>` with `{"path":"<path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. The registry binds exact decision content. A substantive postapproval edit increments `RNN` and needs new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Neither a Markdown status nor old approval of different content is authority. Do not approve on the user's behalf.
