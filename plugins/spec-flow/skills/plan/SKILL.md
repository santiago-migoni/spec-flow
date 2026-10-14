---
name: plan
description: "Plan the technical delivery of an approved release spec against shared decisions."
---

# Spec-Flow: plan

<HARD-GATE>
Require current registry approval of release spec and its roadmap and strategic dependencies. Run gate for plan; unresolved material spec questions block planning.
</HARD-GATE>

Read approved spec and applicable architecture, structure, infrastructure, and constitution. Inspect current code. Write .specs/release-vX.Y.Z/plan.md using assets/plan-template.md. The plan owns solution choices, phase boundaries in the canonical `phases` array (`id`, `description`, `depends_on`), deliverables, dependencies, file scope, and risk response for this release. Refer to strategic decision IDs rather than copying them. Do not repeat task-level commands or acceptance criteria prose; link to AC IDs.

The contract uses kind plan, id PLAN-X.Y.Z, revision R00, and an exact-digest depends_on entry for this release's spec path. Include shared documents whose decisions directly shape the plan. Check every applicable constitution MUST, each spec nonfunctional requirement, and each AC's planned delivery. Flag conflicts; a MUST violation blocks tasks. Validate and request approval.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>. Use validate with {"path":"..."} or {"release":"vX.Y.Z"}, digest with {"path":"..."}, gate with {"kind":"<phase>","release":"vX.Y.Z"}, and status with {}. Registry approval of the exact decision digest controls gates; a Markdown status is only a view. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Do not silently convert historical approvals or checked boxes.

Validate the resulting document. Present its concrete draft for human approval. On explicit approval call approve with {"path":"<project-relative path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}. A substantive edit after approval increments RNN and requires new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Do not approve on behalf of the user.
