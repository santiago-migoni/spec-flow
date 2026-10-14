---
name: roadmap
description: "Prioritize outcomes and group stories into explicit SemVer releases using approved strategy."
---

# Spec-Flow: roadmap

<HARD-GATE>
Inspect project configuration and .specs first. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for this phase and obey it. Urgency never waives a failed gate. Require current registry approval of constitution and applicable shared design. Do not start a release spec until the roadmap selects its vX.Y.Z release and is approved.
</HARD-GATE>

Read approved strategy and backlog. Write `.specs/roadmap.md` using `assets/roadmap-template.md`. It owns priorities, sequence, outcome targets, release grouping, and selected release identifiers in the canonical `releases` array with `version`, `objective`, and `status`. Do not duplicate the sequence in prose. Use strict numeric `vX.Y.Z` and one active release at a time, with multiple stories or features allowed in that release. A roadmap entry names intended outcomes; spec owns behavior and acceptance, plan owns the technical solution.

Use `kind: "roadmap"` and an exact-digest constitution dependency; include other shared decisions it relies on. Validate and request approval. A later scope or priority change needs a new revision and approval; it does not automatically authorize execution.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

Present the draft for human approval. On explicit approval, call `approve --input <json-file>` with `{"path":"<path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. The registry binds exact decision content. A substantive postapproval edit increments `RNN` and needs new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Neither a Markdown status nor old approval of different content is authority. Do not approve on the user's behalf.
