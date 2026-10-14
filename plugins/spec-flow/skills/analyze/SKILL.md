---
name: analyze
description: "Read-only cross-check of approved release documents, acceptance coverage, and strategic constraints."
---

# Spec-Flow: analyze

<HARD-GATE>
Require a release spec, plan, and tasks. Run gate for analyze and validate the release; report failed validation instead of treating malformed artifacts as ready.
</HARD-GATE>

Read the release contract chain and decision prose. Report duplication, ambiguity, stale dependencies, uncovered AC IDs, task steps without concrete expected verification, constitution MUST conflicts, and plan/strategy mismatch. Use assets/report-template.md for a conversation-only report, including severity, location, evidence, and suggested correction. Do not write any file or alter approvals. A CRITICAL finding blocks recommending implementation. Offer exact edits for the owner skill to apply after the user authorizes the change; the owner skill validates the changed content and records the user's approval; accepting exact proposed wording is itself approval, without a redundant confirmation. Zero findings is valid; do not invent issues.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>. Use validate with {"path":"..."} or {"release":"vX.Y.Z"}, digest with {"path":"..."}, gate with {"kind":"<phase>","release":"vX.Y.Z"}, and status with {}. Registry approval of the exact decision digest controls gates; a Markdown status is only a view. If legacy NNN-feature-name artifacts exist, stop and run mandatory migrate before writing. For a new unadopted project, run initialize with empty JSON input {} first. Do not silently convert historical approvals or checked boxes.

Analyze is optional and read-only. It does not grant execution authorization or replace the runtime gate.
