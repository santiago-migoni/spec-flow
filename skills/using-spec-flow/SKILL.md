---
name: using-spec-flow
description: "Bootstrap skill for Spec-Driven Development. Invoke this at the start of any session where you intend to work through the SDD cycle: constitution → specify → plan → tasks → implement. Use this whenever the user mentions starting a feature, wants to plan before coding, or says they want to use spec-flow."
---

# Using Spec-Flow

Spec-Flow is an opt-in, spec-driven development workflow. When active, every feature follows a strict artifact chain before any code is written.

<HARD-GATE>
Do NOT write code, scaffold files, or invoke any implementation action until the full artifact chain for the current feature exists: spec.md → plan.md → tasks.md. If any artifact is missing, invoke the corresponding phase skill first.
</HARD-GATE>

## The Seven Phases

```
constitution → specify → plan → tasks → implement → converge → finishing-branch
```

Each phase produces a file in `specs/`. Each phase requires the previous artifact to exist before it can run.

| Phase | Skill | Input | Output | Gate |
|---|---|---|---|---|
| **constitution** | `spec-flow:constitution` | User description of project | `specs/constitution.md` | None — first phase |
| **specify** | `spec-flow:specify` | Feature description | `specs/NNN-feature/spec.md` | `specs/constitution.md` must exist |
| **plan** | `spec-flow:plan` | Feature spec | `specs/NNN-feature/plan.md` | `spec.md` must exist |
| **tasks** | `spec-flow:tasks` | Spec + plan | `specs/NNN-feature/tasks.md` | `plan.md` must exist |
| **implement** | `spec-flow:implement` | Tasks + spec | Code changes | `tasks.md` must exist |
| **converge** | `spec-flow:converge` | Code + spec/plan/tasks | Appends gaps to `tasks.md`, or marks spec as Converged | `tasks.md` must have been through at least one implement pass |
| **finishing-branch** | `spec-flow:finishing-branch` | Converged feature + passing tests | CHANGELOG updated, branch merged or pushed as PR | Spec status must be `Converged` |

## Artifact Layout

```
specs/
├── constitution.md              ← project-wide principles (created once)
├── 001-feature-name/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
└── 002-another-feature/
    ├── spec.md
    ├── plan.md
    └── tasks.md
```

## Ecosystem

Spec-Flow is fully independent. It composes naturally with other plugins if they are installed:
- **Ponytail**: if installed, its minimal-code principles apply automatically during implement — no configuration needed
- **RTK**: if installed, it transparently compresses CLI outputs (git, tests, grep) — no configuration needed

## How to Use This Session

1. If no `specs/constitution.md` exists → invoke `spec-flow:constitution` first
2. To start a new feature → invoke `spec-flow:specify` with a description
3. To continue a feature in progress → invoke the next phase skill for that feature
4. If the user asks to "just code something" without going through the flow → remind them Spec-Flow is active and ask which phase to start from, or if they want to skip the flow for this task

## Anti-Patterns

| Thought | Reality |
|---|---|
| "This feature is too small to need a spec" | Small features are where assumptions waste the most time. A spec can be 10 lines. |
| "I remember what the plan said" | Read `plan.md`. Memory drifts; the file doesn't. |
| "Let me just start coding and spec later" | Spec-Flow exists to prevent this. No code before `tasks.md`. |
| "The tasks are obvious, I'll skip tasks.md" | Without `tasks.md`, implement has no checkpoint mechanism. |
