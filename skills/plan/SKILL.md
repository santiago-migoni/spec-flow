---
name: plan
description: "Translate a feature spec into a concrete implementation plan: architecture, tech choices, project structure, and data contracts — all cross-checked against the project constitution. Use this after spec.md is approved and before breaking work into tasks."
model: opus
effort: high
---

# Spec-Flow: Plan

Turn a spec into an implementation blueprint. The plan defines HOW, while the spec defined WHAT.

<HARD-GATE>
Before proceeding:
1. `.specs/constitution.md` must exist — if not, stop and invoke `spec-flow:constitution`
2. A `spec.md` must exist for the current feature — if not, stop and invoke `spec-flow:specify`
3. No `[NEEDS CLARIFICATION]` markers should remain open in `spec.md` — resolve them with the user before planning
</HARD-GATE>

## When to Run This Phase

- After `spec.md` is written and approved
- When the implementation approach needs to be decided before breaking into tasks

## Process

1. **Read `.specs/constitution.md`** and `.specs/NNN-feature-name/spec.md`
2. **Explore the current codebase** — understand existing patterns, file structure, dependencies already in use
3. **Draft the plan** — use `assets/plan-template.md` as the output format. Frontmatter `code` is `PLAN-NNN` (same `NNN` as the feature directory), `version` is `R00`.
4. **Constitution check** — for every principle section in `.specs/constitution.md` (`Code Principles`, `Security`, `Operational Principles`, `Observability`, `Performance`, `Dependency Policy`), verify this plan doesn't violate a `MUST` and states a reason for any `SHOULD` deviation. Flag any conflict explicitly — a `MUST` violation blocks moving to `tasks` until resolved.
5. **NFR check** — for every entry in `spec.md`'s `Non-Functional Requirements`, confirm the architecture satisfies it or flag it as unaddressed.
6. **Write `.specs/NNN-feature-name/plan.md`**
7. **Summarize and confirm** — report an executive summary (150 words max, never the full document) of what was written, then ask for approval or revisions
8. **On revision request, before approval** — edit `plan.md` directly, then repeat step 7. This loop never changes `Version` — it stays `R00` no matter how many times it repeats, because the document hasn't been approved yet. Only an edit requested **after** the user already approved this plan increments `Version` by one.

## Quality Check Before Writing

- [ ] Every file path in the structure refers to a real location in the repo (or explicitly "new file")
- [ ] No dependency listed contradicts the constitution's constraints
- [ ] `Constitution Check` covers every principle section that applies — no unaddressed `MUST`, no unexplained `SHOULD` deviation
- [ ] `NFR Compliance` addresses every Non-Functional Requirement in `spec.md`, or the section is "N/A"
- [ ] The plan addresses every user story in `spec.md`
- [ ] No implementation detail that Ponytail would flag as over-engineering (prefer the native/simple path)
- [ ] A Mermaid diagram is present only if the architecture has more than one component/interaction to show

## After Writing

Tell the user: "Plan written to `.specs/NNN-feature-name/plan.md`. Run `spec-flow:tasks` to break this into executable tasks."
