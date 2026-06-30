---
name: constitution
description: "Create or update the project constitution — the single source of truth for principles, tech stack, and standards that all subsequent phases must respect. Use this whenever starting a new project with spec-flow, or when the tech stack or core principles change."
---

# Spec-Flow: Constitution

The constitution is a per-project file that defines what is true about this project before any feature work begins. Every `plan` phase cross-checks against it.

<HARD-GATE>
This is the first phase — no gate. But do NOT proceed to `spec-flow:specify` until `specs/constitution.md` exists and the user has reviewed it.
</HARD-GATE>

## When to Run This Phase

- First time Spec-Flow is used in a project (no `specs/constitution.md` exists)
- When the project's tech stack, principles, or constraints change significantly
- When a `plan` phase reveals a conflict with unstated principles

## Process

1. **Check for existing constitution** — read `specs/constitution.md` if it exists (this may be an update, not a creation)
2. **Explore the project** — read `README.md`, `CLAUDE.md`, `package.json` / `Cargo.toml` / `pyproject.toml`, and any other root config files to infer the current stack and conventions
3. **Ask targeted questions** — only about things that can't be inferred from the codebase; one question at a time
4. **Draft the constitution** — use `assets/constitution-template.md` as the output format
5. **Present for review** — show the draft to the user and get explicit approval before writing the file
6. **Write `specs/constitution.md`** — create the `specs/` directory if needed

## After Writing

Tell the user: "Constitution written to `specs/constitution.md`. You can now run `spec-flow:specify` to start a feature."
