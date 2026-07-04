---
name: constitution
description: "Create or update the project constitution — the single source of truth for principles, tech stack, and standards that all subsequent phases must respect. Use this whenever starting a new project with spec-flow, or when the tech stack or core principles change."
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
5. **Write `.specs/constitution.md`** — create the `.specs/` directory if needed
6. **Summarize and confirm** — report an executive summary (150 words max, never the full document) of what was written, then ask for approval or revisions
7. **On revision request** — edit `.specs/constitution.md` directly, then repeat step 6 with a summary of what changed

## After Writing

Tell the user: "Constitution written to `.specs/constitution.md`. You can now run `spec-flow:specify` to start a feature."
