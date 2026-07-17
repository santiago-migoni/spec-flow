# Spec: [Feature Name]

<!-- Every claim in this document must be measurable or falsifiable — avoid vague adjectives ("fast", "robust", "intuitive", "seamless") without a concrete threshold or test. spec-flow:analyze flags unmeasurable language as an Ambiguity finding. -->

| Name   | Code       | Version              | Date         | Status                        |
| ---    | ---        | ---                  | ---          | ---                           |
| [name] | SPEC-[NNN] | [R00, R01, R02, ...] | [YYYY-MM-DD] | [Draft, Approved, Converged]  |

## Summary

[One sentence: what this feature does and why it exists]

## Success Metrics

<!-- How you'll know this feature worked, beyond "the acceptance scenarios passed" — a business or usage outcome. Skip if this feature has no measurable outcome beyond correctness; write "N/A" rather than inventing one. -->

- [Metric]: [target] — [how it's measured, e.g., "Checkout completion rate: +5% within 30 days — tracked via analytics funnel"]

## User Stories

<!-- One block per story, ordered by priority. P1 = must-ship, P2 = should-ship, P3 = nice-to-have. Repeat as US2, US3, ... for each additional story. -->

### US1 — [Title] (P1)

[Describe the scenario in plain language]

**Acceptance Scenarios**:

- **Given** [initial state], **When** [action], **Then** [expected outcome]
- **Given** [initial state], **When** [action], **Then** [expected outcome]

## Non-Functional Requirements

<!-- Feature-specific quality bar, additive to constitution.md's global MUSTs — don't repeat a constitution principle here, only what this feature specifically needs. Write "N/A" if the constitution's baseline already covers this feature with no exceptions. -->

- **MUST**: [e.g., "Search results return within 200ms at P95"]
- **SHOULD**: [e.g., "Degrade to cached results if the search index is unavailable"]

## Edge Cases

- [Edge case 1 and expected behavior]
- [Edge case 2 and expected behavior]

## Assumptions & Dependencies

<!-- External systems, prior specs, or data this feature assumes already exist. Write "None" if there are none. -->

- [e.g., "Assumes .specs/003-user-auth is implemented and session tokens are available"]

## Explicit Non-Goals

- [Thing this feature intentionally does NOT do]

## Open Questions

<!-- Empty section is a valid, finished state — don't invent a question to fill it. -->

- [NEEDS CLARIFICATION: question that must be answered before planning]
