---
name: backlog
description: "Capture an idea, deferred task, or future feature into .specs/backlog.md without derailing current work. Use this whenever the user says to note something for later, add to the backlog, or park an idea — during any phase, or with no phase active. Items are removed automatically once spec-flow:specify turns them into a spec."
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

1. **Read `.specs/backlog.md`** if it exists — create it fresh from `assets/backlog-template.md` if it doesn't
2. **Determine the next backlog ID** — `B` + zero-padded 3-digit number, one greater than the highest existing `BNNN` across all priority sections (or `B001` if empty)
3. **Ask the priority** — P0 (critical), P1 (high), P2 (medium), or P3 (low). Default to P2 if the user doesn't say
4. **Append one line** to the end of the matching `## PN` section: `- [ ] BNNN <one-line description> (noted <today's date>, from <phase or context>)`
5. **Write `.specs/backlog.md`**

## Format Rules

- One line per item — if it needs more than one sentence, it's not backlog material, it's a feature; run `spec-flow:specify` instead
- The file is ordered by priority section (P0 top, P3 bottom); within a section, order is chronological
- P0 is reserved for critical items — something broken or blocking, not just important
- Never reorder, edit, or delete existing lines, except: `spec-flow:specify` consuming one (see Consumption below), or moving a line to a different `## PN` section on explicit reprioritization request

## Consumption

`spec-flow:specify` checks `.specs/backlog.md` at the start of a new feature. If the feature being specified corresponds to an existing backlog line, that line is deleted once `spec.md` is written — the backlog item has been "processed."

## After Writing

Tell the user: "Added to backlog: BNNN (PN) — <description>." Do not show the full file.
