# spec-flow

A Claude Code plugin for Spec-Driven Development. Every feature follows a strict artifact chain before any code is written: constitution → specify → plan → tasks → implement → converge → finishing-branch.

## Why

AI coding assistants are fast at generating code and slow at recovering from wrong assumptions. Spec-Flow forces the thinking to happen first — in plain text, in your repo, under version control. By the time code is written, the spec, plan, and task list are all there as ground truth.

## The Seven Phases

```
constitution → specify → plan → tasks → implement → converge → finishing-branch
```

| Phase | Skill | Output | Gate |
|---|---|---|---|
| **constitution** | `spec-flow:constitution` | `specs/constitution.md` | None — first phase |
| **specify** | `spec-flow:specify` | `specs/NNN-feature/spec.md` | constitution must exist |
| **plan** | `spec-flow:plan` | `specs/NNN-feature/plan.md` | spec must exist |
| **tasks** | `spec-flow:tasks` | `specs/NNN-feature/tasks.md` | plan must exist |
| **implement** | `spec-flow:implement` | Code changes | tasks must exist |
| **converge** | `spec-flow:converge` | Gap analysis appended to tasks | implement must have run |
| **finishing-branch** | `spec-flow:finishing-branch` | CHANGELOG + merge/PR options | spec status must be `Converged` |

### Artifact layout

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

## Installation

### Claude Desktop

Download the latest `.plugin` file from [Releases](../../releases) and open it in Claude Desktop.

### Claude Code CLI

```bash
claude plugin marketplace add https://github.com/santiago-migoni/spec-flow
claude plugin install spec-flow
```

To install only for the current project:

```bash
claude plugin install spec-flow --scope project
```

## Usage

Start a session by invoking the bootstrap skill:

```
/spec-flow:using-spec-flow
```

From there, Claude will guide you through the phases in order. Each phase skill can also be invoked directly:

```
/spec-flow:constitution     ← first time on a new project
/spec-flow:specify          ← start a new feature
/spec-flow:plan             ← after spec is written
/spec-flow:tasks            ← after plan is written
/spec-flow:implement        ← execute the task list
/spec-flow:converge         ← gap analysis after implementation
/spec-flow:finishing-branch ← tests, changelog, merge or PR
```

## Ecosystem

Spec-Flow is fully independent and composes naturally with other plugins if installed:

- **[Ponytail](https://github.com/DietrichGebert/ponytail)** — its minimal-code principles apply automatically during implement
- **[RTK](https://github.com/rtk-ai/rtk)** — transparently compresses CLI outputs during implement and finishing-branch

No configuration needed for either. They activate on their own if present.

## License

MIT
