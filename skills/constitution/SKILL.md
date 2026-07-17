---
name: constitution
description: "Create or update the project constitution — the single source of truth for principles, tech stack, and standards that all subsequent phases must respect. Use this whenever starting a new project with spec-flow, or when the tech stack or core principles change."
model: opus
effort: high
---

# Spec-Flow: Constitution

The constitution is a per-project file that defines what is true about this project before any feature work begins. Every `plan` phase cross-checks against it.

<HARD-GATE>
This is the first phase — no gate. But do NOT proceed to `spec-flow:specify` until `.specs/constitution.md` exists and the user has reviewed it.
</HARD-GATE>

## When to Run This Phase

- First time Spec-Flow is used in a project (no `.specs/constitution.md` exists)
- When the project's tech stack, principles, or constraints change significantly
- When a `plan` phase reveals a conflict with unstated principles

## Process

1. **Check for existing constitution** — read `.specs/constitution.md` if it exists (this may be an update, not a creation)
2. **Explore the project** — read `README.md`, `CLAUDE.md`, `package.json` / `Cargo.toml` / `pyproject.toml`, and any other root config files to infer the current stack and conventions
3. **Ask targeted questions** — only about things that can't be inferred from the codebase; one question at a time
4. **Draft the constitution** — use `assets/constitution-template.md` as the output format
5. **Write `.specs/constitution.md`** — create the `.specs/` directory if needed. The document-control table's `Version` is `R00` and `Status` is `Draft` for a brand-new constitution.
6. **Summarize and confirm** — report an executive summary (150 words max, never the full document) of what was written, then ask for approval or revisions
7. **On revision request, before approval** — edit `.specs/constitution.md` directly, then repeat step 6. This loop never changes `Version` or `Status` — they stay `R00`/`Draft` (or whatever they already were) no matter how many times it repeats, because the document hasn't been approved yet.
8. **On approval** — set `Status` to `Approved` in the document-control table before ending the turn.

## Principle Keywords

`Code Principles`, `Security`, `Operational Principles`, `Observability`, `Performance`, and `Dependency Policy` tag every bullet with an RFC 2119 keyword — `MUST`, `SHOULD`, or `MAY`. This is what makes a principle checkable downstream:

- `MUST` — non-negotiable. `plan` must flag any conflict; `analyze` and `converge` always classify a violation as `CRITICAL`.
- `SHOULD` — strong default. A feature may deviate, but `plan.md` must state the reason.
- `MAY` — optional, left to the implementer's judgment.

If a section genuinely doesn't apply to this project (e.g., no `Security`-relevant surface), write a single bullet: `N/A — <why>`, rather than inventing content to fill the section.

## Versioning

`Version` only increments when the user asks for a change to a constitution that was **already approved** in a previous session (i.e., this run started at step 1 with an existing, previously-approved file — not a same-session draft/revise loop). On that kind of edit:
- If the user must still see the resulting text (the model drafts new wording): set `Status` back to `Draft` while the amendment is drafted/revised, then to `Approved` once the user approves it.
- If the user already saw the exact text and is approving it verbatim (e.g. applying a `spec-flow:analyze` finding's specific recommendation) — that instruction *is* the approval: skip `Draft`, set `Status` straight to `Approved` in the same edit, no second confirmation needed.
- Increment `Version` by one (`R00` → `R01`, etc.) either way.
- Append one line to `## Amendments Log`: `- RNN (YYYY-MM-DD): <what changed and why>` — append-only, never edit or reorder existing lines

## After Writing

Tell the user: "Constitution written to `.specs/constitution.md`. You can now run `spec-flow:specify` to start a feature."
