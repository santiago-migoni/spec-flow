---
name: specify
description: "Specify one selected SemVer release as stories and measurable acceptance criteria."
---

# Spec-Flow: specify

<HARD-GATE>
Require an approved roadmap selecting the explicit vX.Y.Z release and current registry approval of its exact digest. Run gate for specify and the release. If a legacy feature directory or unadopted configuration exists, migrate first. Do not write on the repository default branch.
</HARD-GATE>

Read constitution, roadmap entry, applicable shared design, and backlog. Ask one high-impact question at a time. Resolve the selected release version from the user and roadmap; do not infer it from a directory number. Use .specs/release-vX.Y.Z/spec.md and assets/spec-template.md. Create or switch to a release branch before writing; preserve unrelated work.

The spec owns this release's behavior, user stories, acceptance criteria, edge cases, release-specific nonfunctional requirements, non-goals, and outcome measures. It can include multiple stories but one active release at a time, with multiple stories or features allowed in that release. It does not restate roadmap priorities or architectural decisions. Put structured `stories` (`US-...` ID, title, and description) and `acceptance` (`AC-...` ID, owning story ID, and falsifiable description) in the contract. These arrays are canonical; do not repeat criterion descriptions as a second editable list in Markdown prose. The contract uses kind spec, id SPEC-X.Y.Z, revision R00, nonempty stories and acceptance arrays, and a depends_on entry for the exact roadmap digest. Include other approved strategic sources only when directly used. Keep open questions explicit and resolve material ones before plan.

Run validate with {"release":"vX.Y.Z"} only after spec, plan, and tasks all exist; for this phase validate the spec path alone. Backlog items become linked or removed only after a valid spec draft is written; never claim a release from an unchecked idea.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>. Use validate with {"path":"..."} or {"release":"vX.Y.Z"}, digest with {"path":"..."}, gate with {"kind":"<phase>","release":"vX.Y.Z"}, and status with {}. Registry approval of the exact decision digest controls gates; a Markdown status is only a view. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Do not silently convert historical approvals or checked boxes.

Validate the resulting document. Present its concrete draft for human approval. On explicit approval call approve with {"path":"<project-relative path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}. A substantive edit after approval increments RNN and requires new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Do not approve on behalf of the user.
