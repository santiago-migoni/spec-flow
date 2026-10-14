---
name: tasks
description: "Decompose an approved release plan into ordered tasks and verified steps."
---

# Spec-Flow: tasks

<HARD-GATE>
Require current registry approval of the release plan and its spec/strategy dependencies. Run gate for tasks; do not write tasks against a stale plan.
</HARD-GATE>

Read approved plan and spec. Write .specs/release-vX.Y.Z/tasks.md using assets/tasks-template.md. The contract owns the canonical executable task list. Each task needs stable ID, phase, story, nonempty AC ID references, dependencies, contained project-relative file paths, ordered stable step IDs, and a closure condition. Each step has an action and exactly one verification method: argv command list or specific inspection, plus expected result. Group by story and dependency, include relevant test and verification work, and keep one active release at a time, with multiple stories or features allowed in that release. Do not target .specs, .spec-flow, or .git in task files.

The contract uses kind tasks, id TASKS-X.Y.Z, revision R00, and an exact-digest depends_on entry for plan.md. The release validator checks AC coverage and unknown AC references. Validate the document, then validate the full release with {"release":"vX.Y.Z"}; resolve every failure before approval. Task checkboxes, if shown in a generated block, are a harness view. Manually marking one does not prove completion. Approved tasks and execution authorization are distinct, though one explicit human statement may grant both scopes.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>. Use validate with {"path":"..."} or {"release":"vX.Y.Z"}, digest with {"path":"..."}, gate with {"kind":"<phase>","release":"vX.Y.Z"}, and status with {}. Registry approval of the exact decision digest controls gates; a Markdown status is only a view. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Do not silently convert historical approvals or checked boxes.

Validate the resulting document. Present its concrete draft for human approval. On explicit approval call approve with {"path":"<project-relative path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}. A substantive edit after approval increments RNN and requires new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Do not approve on behalf of the user.
