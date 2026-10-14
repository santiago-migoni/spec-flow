---
name: clarify
description: "Resolve consequential ambiguity in a release spec before planning."
---

# Spec-Flow: clarify

<HARD-GATE>
Require an existing release spec and run gate for clarify. Read its current registry approval before editing; an approved spec must not be changed under the old digest.
</HARD-GATE>

Read the release spec, constitution, and applicable decisions. Ask up to five questions, one at a time, only where answers change scope, acceptance, architecture, data, or testing. Use assets/clarifications-template.md for a dated question/answer section in the spec, and revise the directly affected acceptance or prose so no contradiction remains. Do not create a second editable requirements file.

If the spec was approved, increment its revision and return it to draft while wording is open; get a new explicit approval of the final content and inspect affected downstream pins and adopt a new base only with explicit approval. If the user approved exact proposed wording verbatim, that declaration can approve the resulting revision once validated. If no meaningful ambiguity exists, report clean and make no write.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>. Use validate with {"path":"..."} or {"release":"vX.Y.Z"}, digest with {"path":"..."}, gate with {"kind":"<phase>","release":"vX.Y.Z"}, and status with {}. Registry approval of the exact decision digest controls gates; a Markdown status is only a view. If legacy NNN-feature-name artifacts exist, stop and run mandatory migrate before writing. For a new unadopted project, run initialize with empty JSON input {} first. Do not silently convert historical approvals or checked boxes.

Validate the resulting document. Present its concrete draft for human approval. On explicit approval call approve with {"path":"<project-relative path>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}. A substantive edit after approval increments RNN and requires new approval; inspect affected downstream pins and adopt a new base only with explicit approval. Do not approve on behalf of the user.
