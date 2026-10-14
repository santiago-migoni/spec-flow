---
name: using-spec-flow
description: "Start or resume the release-centered Spec-Flow workflow and find the next authorized phase."
---

# Spec-Flow: using-spec-flow

<HARD-GATE>
Inspect project configuration and .specs first. If legacy NNN-feature-name artifacts exist, stop and run mandatory migrate before writing. For a new unadopted project, run initialize with empty JSON input {} first. Run the runtime gate for the intended document or execution phase and obey it; using-spec-flow itself is not a gate kind. Urgency never waives a failed gate.
</HARD-GATE>

Strategy: `constitution → applicable shared system design → roadmap`. Delivery: `specify → clarify (optional) → plan → tasks → analyze (optional) → implement → converge → review-release → finishing-branch`. Create architecture, structure, and infrastructure documents only when applicable to planned releases; record N/A with a reason in the roadmap when omitted. Strategy files are `.specs/{constitution,architecture,structure,infrastructure,roadmap}.md`. An active release uses `.specs/release-vX.Y.Z/{spec,plan,tasks}.md` and may contain multiple stories. Release identifiers use strict numeric SemVer such as `v2.0.0`.

At session start inspect configuration and .specs, then call `status --input <json-file>` using `{}` and `gate --input <json-file>` for the intended phase. For release gates pass `{"kind":"<phase>","release":"vX.Y.Z"}`. Do not infer authorization from file existence, legacy Status: Approved tables, checked boxes, or urgency. Existing approved sources can be reused only while content digest and scope remain current. Legacy projects run migrate before any new write; new projects run initialize with empty JSON input {}.

Draft the next required document, gain its approval, then proceed to dependent phases. Explicit user execution authorization may cover multiple phases; the runtime and implementation skill still control each task. Approval to execute does not authorize push, merge, publication, or deployment. `$backlog` remains independent.

CLI shape: `python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>`. Operations are `validate` (path or release), `digest` (path), `approve` (path, actor, statement, source), `gate` (kind and optional release), and `status` (optional run_id). Resolve plugin root from the installed skill location. Follow the selected phase skill's own hard gate and stop on any failed gate.

## Runtime and approval

Resolve the plugin root from this installed skill. Run `python3 <plugin-root>/scripts/spec-flow.py --root <project> validate --input <json-file>` with `{"path":"<project-relative path>"}` after writing. Use `digest` with the same input to capture exact dependency digests. One fenced `spec-flow` JSON block holds `schema_version: 1`, `kind`, stable `id`, `revision: "R00"` initially, and `depends_on` references. Decision prose remains outside the block. Only generated progress and optional lowercase `status` may be updated as views.

The relevant document skill owns drafting and approval. Bootstrap does not itself approve or rewrite artifacts.
