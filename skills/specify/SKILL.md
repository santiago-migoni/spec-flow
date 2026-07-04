---
name: specify
description: "Turn a feature idea into a structured spec with user stories, acceptance scenarios, and explicit unknowns. Creates .specs/NNN-feature-name/spec.md. Use this whenever the user describes a feature they want to build, a change to make, or a bug to fix that will take more than 30 minutes."
---

# Spec-Flow: Specify

Transform a feature idea into a concrete, testable specification before any planning or coding begins.

<HARD-GATE>
Check that `.specs/constitution.md` exists before proceeding. If it does not exist, stop and invoke `spec-flow:constitution` first.
</HARD-GATE>

## When to Run This Phase

- Starting any new feature, change, or bug fix that will take more than 30 minutes
- When a user says "I want to build X", "add Y", "change Z"

## Process

1. **Read `.specs/constitution.md`** — understand project principles and constraints before asking anything
2. **Determine the feature number** — run `scripts/next-feature-number.sh` from the project root to get the next zero-padded NNN
3. **Check `.specs/backlog.md`** — if it exists, scan for an item related to this feature and use it as context (skip silently if the file doesn't exist yet)
4. **Ask clarifying questions** — one at a time. Focus on: purpose, who benefits, success criteria, edge cases, explicit non-goals. Mark anything unclear as `[NEEDS CLARIFICATION: <specific question>]` in the draft rather than guessing.
5. **Draft `spec.md`** — use `assets/spec-template.md` as the output format
6. **Create `.specs/NNN-feature-name/` directory and write `spec.md`**
7. **Remove the backlog item** — if this spec was drafted from a `.specs/backlog.md` entry, delete that line now
8. **Summarize and confirm** — report an executive summary (150 words max, never the full document) of what was written, then ask for approval or revisions
9. **On revision request** — edit `spec.md` directly, then repeat step 8 with a summary of what changed

## Naming Convention

Feature directory name: `NNN-short-description` (e.g., `003-user-authentication`)
- `NNN`: zero-padded 3-digit number from `scripts/next-feature-number.sh`
- `short-description`: kebab-case, 2-4 words, describes the feature not the implementation

## Quality Check Before Writing

Before saving the file, verify:
- [ ] Every user story has at least one testable acceptance scenario
- [ ] No `[NEEDS CLARIFICATION]` markers remain unless they are intentional open questions for the user to answer
- [ ] The spec does not describe implementation details (HOW) — only behavior (WHAT)
- [ ] Nothing in the spec contradicts `.specs/constitution.md`

## After Writing

Tell the user: "Spec written to `.specs/NNN-feature-name/spec.md`. Run `spec-flow:clarify` first if anything is ambiguous (recommended, not required), or `spec-flow:plan` directly when ready."
