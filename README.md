# spec-flow

Spec-Flow is a Codex plugin for Spec-Driven Development. It guides a feature through an approved chain of versioned artifacts before implementation: constitution → specify → plan → tasks → implement → converge → finishing-branch.

## Why

AI coding assistants are fast at generating code and slow at recovering from wrong assumptions. Spec-Flow makes the spec, plan, and task list the source of truth before code is written, so implementation can be checked against reviewed intent rather than conversation memory.

## The Seven Phases

| Phase | Skill | Output | Gate |
|---|---|---|---|
| **constitution** | `$constitution` | `.specs/constitution.md` | None — first phase |
| **specify** | `$specify` | `.specs/NNN-feature/spec.md` | Constitution must exist |
| **plan** | `$plan` | `.specs/NNN-feature/plan.md` | Spec must exist and be approved |
| **tasks** | `$tasks` | `.specs/NNN-feature/tasks.md` | Plan must exist and be approved |
| **implement** | `$implement` | Code changes | Approved task list must exist |
| **converge** | `$converge` | Gap analysis appended to tasks | Implement must have run |
| **finishing-branch** | `$finishing-branch` | Changelog and integration options | Spec status must be `Converged` |

## Optional Skills

These skills are outside the seven-phase gate chain. They are recommended and never required.

| Skill | Run when | Output |
|---|---|---|
| `$clarify` | After `specify`, before `plan` | Up to five questions answered in `spec.md`'s `## Clarifications` section |
| `$analyze` | After `tasks`, before `implement` | Read-only consistency report across `spec.md`, `plan.md`, and `tasks.md` |
| `$backlog` | Whenever an idea should be parked | Adds an item to `.specs/backlog.md`; `specify` removes a matching item when it becomes a feature |

### Artifact layout

```text
.specs/
├── constitution.md
├── backlog.md
├── 001-feature-name/
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
└── 002-another-feature/
    ├── spec.md
    ├── plan.md
    └── tasks.md
```

## Install from GitHub marketplace

Install the stable marketplace from GitHub:

```bash
codex plugin marketplace add santiago-migoni/spec-flow --ref main
codex plugin add spec-flow@spec-flow
```

Both commands resolve the marketplace and plugin package from GitHub `main`. Installation does not use a local checkout of this repository. The marketplace catalog is at `.agents/plugins/marketplace.json`; its `git-subdir` source points to `plugins/spec-flow/` at `main`.

Codex CLI can list configured marketplaces with `codex plugin marketplace list` and refresh them with `codex plugin marketplace upgrade spec-flow`. GitHub access is required to add or refresh the marketplace and retrieve the package; the installed skills do not call external services at runtime.

## Use in Codex

In Codex CLI, run `/skills` to see available plugin skills, or type `$` to select one. Start with `$using-spec-flow` for an overview, or mention a phase skill such as `$constitution` or `$specify` directly. Codex can also select a skill when your request matches its description.

Each gated skill checks its previous artifact before proceeding. The bundled approval hook adds a guard for supported local patch writes to `.specs/spec.md`, `plan.md`, and `tasks.md`. Codex only runs plugin hooks after the user reviews and trusts them; the prose hard gates remain required, and the hook does not cover shell commands or every specialized write path.

## Ecosystem

Spec-Flow is independent and works alongside other plugins when present:

- **[Ponytail](https://github.com/DietrichGebert/ponytail)** — its minimal-code principles apply during implementation.
- **[RTK](https://github.com/rtk-ai/rtk)** — transparently compresses CLI output during implementation and branch finishing.

Neither is required.

## License

GNU AGPLv3 — see [LICENSE](LICENSE) for details.
