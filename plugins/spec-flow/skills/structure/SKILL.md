---
name: structure
description: "Define code organization and placement conventions from approved shared architecture."
---

# Spec-Flow: structure

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval of constitution and any architecture decision this structure relies on.
</HARD-GATE>

Inspect the repository tree and approved architecture. If this document is not applicable, record N/A with a reason in the roadmap and make no filler document. Write `.specs/structure.md` using `assets/structure-template.md`. It owns module boundaries, directory purposes, placement rules, naming, and dependency direction. Refer to architecture IDs instead of restating component responsibilities. Distinguish existing paths from proposed paths.

Use `kind: "structure"` with exact-digest dependencies on constitution and any architecture decision used. Validate and request approval.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

Present the draft for human approval. On explicit approval, call `approve --input <json-file>` with `{"path":"<path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. The registry binds exact decision content. A substantive postapproval edit increments `RNN` and needs new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Neither a Markdown status nor old approval of different content is authority. Do not approve on the user's behalf.
