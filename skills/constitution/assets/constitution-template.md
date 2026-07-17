# Project Constitution

<!-- Code Principles, Security, Operational Principles, Observability, Performance, and Dependency Policy tag every bullet with an RFC 2119 keyword:
MUST — non-negotiable; plan/analyze/converge treat a violation as CRITICAL.
SHOULD — strong default; a deviation needs a stated reason in plan.md.
MAY — optional, contributor's judgment call.
If a whole section doesn't apply to this project, replace its bullets with one line: N/A — <why>. -->

| Name   | Version              | Date         |
| ---    | ---                  | ---          |
| [name] | [R00, R01, R02, ...] | [YYYY-MM-DD] |

## Purpose

[One paragraph: what this project does and who it's for]

## Tech Stack

- **Language**: [e.g., TypeScript 5.x]
- **Runtime / Framework**: [e.g., Node.js 22, Express]
- **Database**: [e.g., PostgreSQL 16 via Drizzle ORM, or "N/A"]
- **Testing**: [e.g., Vitest, or "N/A"]
- **Linting / Formatting**: [e.g., ESLint + Prettier, or "N/A"]

## Code Principles

- **MUST**: [e.g., "All public functions have at least one test"]
- **SHOULD**: [e.g., "Prefer native platform APIs over third-party libraries (Ponytail philosophy)"]
- **MAY**: [e.g., "Use a functional style where it doesn't hurt readability"]

## Security

<!-- Trust-boundary rules this codebase always follows — not a full threat model. -->

- **MUST**: [e.g., "Never log secrets, tokens, or full request bodies containing PII"]
- **MUST**: [e.g., "Validate and sanitize all input at the API boundary before it reaches business logic"]
- **SHOULD**: [e.g., "Prefer parameterized queries over string-built SQL"]

## Operational Principles

<!-- How this system is deployed, rolled back, and recovered — day-two concerns that shape architecture before day one is over. -->

- **MUST**: [e.g., "Database migrations must be backward compatible — old and new code run against the same schema during rollout"]
- **MUST**: [e.g., "Every deploy is rollback-able within [X] minutes without data loss"]
- **SHOULD**: [e.g., "Roll out changes to a critical path behind a feature flag before 100% exposure"]

## Observability

<!-- What gets logged or measured, and how a failure surfaces — keeps plan.md from inventing conventions per feature. -->

- **MUST**: [e.g., "Every unhandled error is logged with a stack trace and request context"]
- **SHOULD**: [e.g., "Use structured (JSON) logging, not string concatenation"]

## Performance

<!-- Budgets and defaults that shape architecture decisions — not a full perf spec, just what plan.md must respect by default. -->

- **MUST**: [e.g., "p95 response time under 300ms for user-facing endpoints"]
- **SHOULD**: [e.g., "Avoid N+1 queries in hot paths"]
- **MAY**: [e.g., "Optimize only after profiling shows a measured bottleneck — no speculative performance work"]

## Dependency Policy

<!-- When plan.md may reach for a new package. -->

- **MUST**: [e.g., "Check the standard library and already-installed dependencies before adding a new package"]
- **SHOULD**: [e.g., "Prefer dependencies with no transitive dependencies of their own"]

## Naming Conventions

- [e.g., "Files: kebab-case. Classes: PascalCase. Functions: camelCase."]

## Constraints

- [e.g., "Must run offline", "No paid dependencies", "Must support Node 18+"]

## Out of Scope

- [Things explicitly excluded — prevents scope creep during plan phases]

## Amendments Log

<!-- Append-only — never edit or reorder existing lines. One line per revision made after this constitution was first approved. Format: - RNN (YYYY-MM-DD): <what changed and why> -->
