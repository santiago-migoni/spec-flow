---
name: backlog
description: "Record deferred ideas without changing release scope or approval."
---

# Spec-Flow: backlog

<HARD-GATE>
No phase prerequisite. Inspect adoption and legacy status before writing; migration is mandatory for legacy projects.
</HARD-GATE>

Read .specs/backlog.md, creating it from assets/backlog-template.md if absent. Add one stable BNNN item with date, source, priority, and concise idea. Default to P2 only when priority is genuinely unspecified. Preserve existing items and priority order; explicit reprioritization may move an item. A backlog entry is not a roadmap decision, selected release, approved spec, or execution authorization. When an approved roadmap selects an item, link it to the release; remove it only after a valid spec draft records the idea. Report the item ID and priority.

## Runtime discipline

Resolve <plugin-root> from this installed SKILL.md. Run python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>. Use validate with {"path":"..."} or {"release":"vX.Y.Z"}, digest with {"path":"..."}, gate with {"kind":"<phase>","release":"vX.Y.Z"}, and status with {}. Registry approval of the exact decision digest controls gates; a Markdown status is only a view. If legacy `.specs/NNN-name/` folders exist, stop before writing and follow the `migrate-preview` → review → `migrate-apply` flow in `$using-spec-flow`; use `migrate-resume` after an interrupted apply. For a new unadopted project, run initialize with empty JSON input {} first. Do not silently convert historical approvals or checked boxes.

The backlog is a side channel and gates nothing. It never bypasses migration or approval of release work.
