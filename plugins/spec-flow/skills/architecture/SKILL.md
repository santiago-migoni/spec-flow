---
name: architecture
description: "Define shared system context, quality goals, components, contracts, data flows, and architectural decisions from an approved constitution."
---

# Spec-Flow: architecture

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval for the exact constitution digest; a Markdown label is insufficient.
</HARD-GATE>

Read the approved constitution, current code, and relevant existing design evidence. Write `.specs/architecture.md` using [the architecture template](assets/architecture-template.md). This document owns shared system boundaries, components, responsibilities, contracts, data ownership/flow, quality goals, and cross-release technical decisions. Refer to constitution principles without copying them.

Recommended elaboration order is architecture → infrastructure → structure, with only applicable documents. Inspect existing structure and operational constraints from the start; findings may require revisiting architecture. This order is not a mandatory dependency chain. If architecture is inapplicable, create no filler document; record N/A with a reason when drafting the roadmap under its own gate.

## Drafting and review

Use all eleven template sections: purpose/audience/scope; system context/boundaries; current evidence/intended design; quality goals/constraints; solution strategy; components/contracts; data/runtime scenarios; crosscutting concepts; decisions/consequences; risks/debt/questions; references/amendments. Explain N/A for inapplicable sections.

Choose only diagrams that answer a reader's question. Context and application/data-store views may suffice; add component or interaction detail when needed. Give components stable IDs and quality goals observable scenarios and verification approaches. Cover important failure paths and data ownership. Record significant decisions with ID, context, alternatives, choice, rationale, consequences, and conditions for review; link existing ADRs rather than requiring separate files.

Design enough to support upcoming work. Ask for unknown human decisions and leave assumptions or unanswered questions explicit. Distinguish verified implementation, proposed changes, and approved design; approval does not prove implementation. Evidence must identify its source and scope. Keep repository placement in structure, deployment/operations in infrastructure, priorities in roadmap, and release implementation detail in release plans. Do not require or create later documents to finish this one; add navigational references when available.

Revisit when boundaries, interfaces, quality goals, or significant decisions change. Preserve superseded decision history and inspect affected dependents. Document approval does not authorize implementation, deployment, integration, or publication.

This is a Spec-Flow adaptation of [PMI's agile documentation guidance](https://www.pmi.org/disciplined-agile/agile/documentation), [Agile Alliance's continuous design guidance](https://agilealliance.org/glossary/simple-design/), [arc42](https://arc42.org/overview/), [C4](https://c4model.com/diagrams), and [architecture decision records](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), not an official template from those sources.

Use `kind: "architecture"` and a `depends_on` entry with the project-relative constitution path and its exact digest. Pin any other approved strategic source actually used, requiring its current registry approval before relying on it. Keep the dependency graph acyclic: feedback may trigger a revision, not reciprocal pins. Do not add a dependency solely for a navigational link. Validate and request approval before dependent design work.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

Present the draft for human approval. On explicit approval, call `approve --input <json-file>` with `{"path":"<path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. The registry binds exact decision content. A substantive postapproval edit increments `RNN` and needs new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Neither a Markdown status nor old approval of different content is authority. Do not approve on the user's behalf.
