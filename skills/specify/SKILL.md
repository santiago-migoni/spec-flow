---
name: specify
description: "Turn a feature idea into a structured spec with user stories, acceptance scenarios, and explicit unknowns. Creates .specs/NNN-feature-name/spec.md. Use this whenever the user describes a feature they want to build, a change to make, or a bug to fix that will take more than 30 minutes."
model: opus
effort: high
---

# Spec-Flow: Specify

Transform a feature idea into a concrete, testable specification before any planning or coding begins.

<HARD-GATE>
Check that `.specs/constitution.md` exists before proceeding. If it does not exist, stop and invoke `spec-flow:constitution` first.

Never write `spec.md` while checked out on the repo's default branch (the remote's HEAD, typically `main` or `master`). Create and check out a feature branch first — see step 6 below.
</HARD-GATE>

## When to Run This Phase

- Starting any new feature, change, or bug fix that will take more than 30 minutes
- When a user says "I want to build X", "add Y", "change Z"

## Process

1. **Read `.specs/constitution.md`** — understand project principles and constraints before asking anything
2. **Determine the feature number** — run `scripts/next-feature-number.sh` from the project root to get the next zero-padded NNN
3. **Check `.specs/backlog.md`** — if it exists, scan for an item related to this feature and use it as context (skip silently if the file doesn't exist yet)
4. **Ask clarifying questions** — one at a time. Focus on: purpose, who benefits, measurable success criteria, feature-specific non-functional requirements beyond the constitution's baseline, edge cases, assumptions/dependencies on other systems or specs, and explicit non-goals. Mark anything unclear as `[NEEDS CLARIFICATION: <specific question>]` in the draft rather than guessing.
5. **Draft `spec.md`** — use `assets/spec-template.md` as the output format. The document-control table's `Code` is `SPEC-NNN` (same `NNN` as the feature directory), `Version` is `R00`, `Status` is `Draft`.
6. **Ensure a feature branch is active** — get the repo's default branch (`git symbolic-ref refs/remotes/origin/HEAD` stripped of `refs/remotes/origin/`, falling back to `main`/`master` if no remote is configured) and the current branch (`git branch --show-current`). If they match, create and check out a new branch named exactly like the feature directory: `git checkout -b NNN-short-description`. Never proceed to the next step while still on the default branch.
7. **Create `.specs/NNN-feature-name/` directory and write `spec.md`**
8. **Remove the backlog item** — if this spec was drafted from a `.specs/backlog.md` entry, delete that line now
9. **Summarize and confirm** — report an executive summary (150 words max, never the full document) of what was written, then ask for approval or revisions
10. **On revision request, before approval** — edit `spec.md` directly, then repeat step 9. This loop never changes `Version` or `Status` — they stay `R00`/`Draft` no matter how many times it repeats, because the document hasn't been approved yet. Only an edit requested **after** the user already approved this spec increments `Version` by one.
11. **On approval** — set `Status` to `Approved` in the document-control table before ending the turn. (`Status` later becomes `Converged`, but only `spec-flow:converge` sets that.)
12. **On any edit requested after approval** — two cases:
    - The user must still see the resulting text (an open-ended change, the model drafts new content): reset `Status` to `Draft` before editing (this is what triggers the `Version` bump in step 10), then repeat step 11 once the user approves the result.
    - The user already saw the exact text and is approving it verbatim (e.g. applying a `spec-flow:analyze` finding's specific recommendation) — that instruction *is* the approval: skip `Draft`, bump `Version`, and set `Status` straight to `Approved` in the same edit. Do not ask for a second confirmation.

## Naming Convention

Feature directory name: `NNN-short-description` (e.g., `003-user-authentication`)
- `NNN`: zero-padded 3-digit number from `scripts/next-feature-number.sh`
- `short-description`: kebab-case, 2-4 words, describes the feature not the implementation — this is also the document-control table's `Name` value

## Quality Check Before Writing

Before saving the file, verify:
- [ ] Every user story has at least one testable acceptance scenario
- [ ] Success Metrics and Non-Functional Requirements are measurable or falsifiable — no vague adjectives without a threshold
- [ ] Non-Functional Requirements only list what's specific to this feature — anything already covered by `.specs/constitution.md`'s baseline stays out
- [ ] No `[NEEDS CLARIFICATION]` markers remain unless they are intentional open questions for the user to answer
- [ ] The spec does not describe implementation details (HOW) — only behavior (WHAT)
- [ ] Nothing in the spec contradicts `.specs/constitution.md`

## After Writing

Tell the user: "Spec written to `.specs/NNN-feature-name/spec.md`. Run `spec-flow:clarify` first if anything is ambiguous (recommended, not required), or `spec-flow:plan` directly when ready."
