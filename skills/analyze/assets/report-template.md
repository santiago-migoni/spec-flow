# Analysis: [Feature Name]

<!-- Conversation output only — spec-flow:analyze never writes this to disk. Use this shape when presenting results. -->

| Name   | Version              | Date         |
| ---    | ---                  | ---          |
| [name] | [R00, R01, R02, ...] | [YYYY-MM-DD] |

## Findings

<!-- Cap at 30 rows; summarize any overflow in one line beneath the table. Severity, highest first:
CRITICAL — constitution MUST violation, or a P1 story with zero task coverage (always CRITICAL, never downgraded)
HIGH — conflicting/duplicate requirement, untestable acceptance criterion
MEDIUM — terminology drift, missing non-functional coverage
LOW — style, minor redundancy -->

| ID | Category                                                                    | Severity                     | Location       | Summary                | Recommendation |
|--- | ---                                                                         | ---                          | ---            | ---                    | ---            |
| F1 | [Duplication\|Ambiguity\|Coverage gap\Constitution conflict\|Inconsistency] | [CRITICAL\|HIGH\|MEDIUM\LOW] | [file:section] | [one-line description] | [concrete fix] |

## Coverage Summary

<!-- "Requirement" covers both acceptance scenarios (USn/ACn) and spec.md's Non-Functional Requirements — list both kinds here. -->

| Requirement        | Has Task? | Task IDs     |
| ---                | ---       | ---          |
| [US1/AC1]          | [Yes\|No] | [T002, T003] |
| [NFR: description] | [Yes\|No] | [T005]       |

## Metrics

- Total requirements: [N]
- Total tasks: [N]
- Coverage: [N]%
- Findings by severity: [X CRITICAL, Y HIGH, Z MEDIUM, W LOW]

## Next Actions

[If any CRITICAL finding exists: "Resolve CRITICAL findings before spec-flow:implement." Otherwise: "No CRITICAL findings — ready for spec-flow:implement." Zero findings overall is valid — report it as such, don't invent issues to fill the report.]
