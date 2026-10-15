---
name: structure
description: "Define repository maps, module boundaries, placement rules, and naming from applicable approved architecture and infrastructure decisions."
---

# Spec-Flow: structure

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval of constitution and any architecture decision this structure relies on.
</HARD-GATE>

Inspect the repository tree, approved constitution, and applicable approved architecture and infrastructure. Write `.specs/structure.md` using [the structure template](assets/structure-template.md). It owns repository organization, code module boundaries, directory purposes, placement rules, naming, and dependency direction. Reference architectural responsibilities and operational decisions instead of duplicating them.

Recommended elaboration order is architecture → infrastructure → structure, with only applicable documents. Incorporate infrastructure decisions that affect packages, configuration, deployment files, or distribution. Infrastructure is not mandatory: proceed from constitution and the approved design actually needed. If structure is inapplicable, create no filler; record N/A with a reason when drafting the roadmap under its own gate.

## Drafting and review

Use all ten template sections: purpose/audience/scope; verified current organization; architecture-to-repository mapping; intended organization/placement; naming/public interfaces; dependencies/module boundaries; tests/configuration/documentation/resources; generated/third-party/distribution files; decisions/risks/pending changes; references/amendments. Explain N/A for inapplicable sections.

Include an annotated tree in a fenced `text` block based on actual repository inspection. Show important directories and files at a useful depth, describe omitted repetitive content or downloaded dependencies, and do not impose the template's illustrative src/ layout. For a new empty repository, state the verified absence of content. When changes are proposed, provide a separate annotated proposed tree; otherwise state that no layout change is needed and omit the second tree. Never present future paths as verified current paths. Tree output may be assembled from inspected paths; the tree command is not required.

Map components or known responsibilities to paths, current/proposed state, and entry points. Explain where the next change belongs, with placement/naming rules, dependency limits, and available verification mechanisms. Distinguish editable sources, generated outputs, third-party content, and distributable artifacts. Link operational procedures rather than copying them.

Record significant organization decisions with ID, context, alternatives, choice, rationale, consequences, and review conditions, or link existing ADRs. Ask for unknown human choices and leave assumptions/questions explicit. Distinguish proposed and approved design from verified files; approval does not create directories or establish implementation. Revisit when module layout, dependency rules, entry points, or distribution boundaries change and inspect affected dependents. Keep implementation tasks in release plans. Do not require or create future dependent documents to finish this one; design approval does not authorize implementation, integration, or publication.

This Spec-Flow adaptation uses [arc42's building block view](https://docs.arc42.org/section-5/) and [component-to-source descriptions](https://faq.arc42.org/questions/C-5-6/); the tree and placement rules connect those views to the actual repository.

Use `kind: "structure"` with exact-digest dependencies on constitution and any approved architecture or infrastructure decisions actually used. Require current registry approval for all such sources, including infrastructure. Keep the graph acyclic: revisiting a source decision does not justify reciprocal pins. Omit sources not used, even if they exist; navigational links alone are not dependencies. Validate and request approval.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

Present the draft for human approval. On explicit approval, call `approve --input <json-file>` with `{"path":"<path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. The registry binds exact decision content. A substantive postapproval edit increments `RNN` and needs new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Neither a Markdown status nor old approval of different content is authority. Do not approve on the user's behalf.
