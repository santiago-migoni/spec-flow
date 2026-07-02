---
name: backlog
description: "Capture an idea, deferred task, or future feature into specs/backlog.md without derailing current work. Use this whenever the user says to note something for later, add to the backlog, or park an idea — during any phase, or with no phase active. Items are removed automatically once spec-flow:specify turns them into a spec."
---

# Spec-Flow: Backlog

A running, append-only ledger for anything noticed but out of scope right now — a bug, an idea, a deferred feature. Deliberately invoked only; no phase auto-detects backlog-worthy items.

<HARD-GATE>
None — the backlog has no gate and gates nothing. It can be written to from any phase, or with no phase active at all.
</HARD-GATE>

## When to Invoke This Skill

- The user says "note this for later," "add to backlog," "park this," or similar, at any point in a session
- Something out-of-scope surfaces during `implement` or `converge` and isn't worth breaking flow to spec right now

## Process

1. **Read `specs/backlog.md`** if it exists — create it fresh from `assets/backlog-template.md` if it doesn't
2. **Determine the next backlog ID** — `B` + zero-padded 3-digit number, one greater than the highest existing `BNNN` in the file (or `B001` if empty)
3. **Append one line**: `- [ ] BNNN <one-line description> (noted <today's date>, from <phase or context>)`
4. **Write `specs/backlog.md`**

## Format Rules

- One line per item — if it needs more than one sentence, it's not backlog material, it's a feature; run `spec-flow:specify` instead
- Never reorder, edit, or delete existing lines, except when `spec-flow:specify` consumes one (see Consumption below)
- No priority field, no status beyond the checkbox — ordering in the file is chronological, not priority

## Consumption

`spec-flow:specify` checks `specs/backlog.md` at the start of a new feature. If the feature being specified corresponds to an existing backlog line, that line is deleted once `spec.md` is written — the backlog item has been "processed."

## After Writing

Tell the user: "Added to backlog: BNNN — <description>." Do not show the full file.
