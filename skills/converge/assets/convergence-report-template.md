<!-- Two parts below. Part 1 is shown in conversation before anything is written to disk — never written to a file itself. Part 2 is the exact block appended to tasks.md, only if findings exist. -->

## Convergence Findings

<!-- Order: CRITICAL first, then HIGH, MEDIUM, LOW. A constitution MUST violation is always CRITICAL, never downgraded. -->

| ID | Gap Type | Severity | Source | Evidence | Remaining Work |
|---|---|---|---|---|---|
| F1 | [missing\|partial\|contradicts\|unrequested] | [CRITICAL\|HIGH\|MEDIUM\|LOW] | [USn/ACn or plan decision] | [what was found, or not found, in the code] | [imperative next step] |

**Checked**: [N] acceptance scenarios, [M] plan decisions, [K] constitution principles
**Findings**: [X] missing, [Y] partial, [Z] contradicts, [W] unrequested

Ask the user to confirm before appending tasks, unless there are zero findings.

## Appended to tasks.md (only when findings exist)

<!-- M = highest existing task ID in tasks.md, N = highest existing phase number + 1. Never reuse, renumber, or edit an existing task ID. -->

```markdown
## Phase N: Convergence

- [ ] T{M+1} [imperative action] per [source-ref] (missing)
- [ ] T{M+2} [imperative action] per [source-ref] (partial)
```

## When There Are Zero Findings

- `tasks.md` stays byte-for-byte unchanged — do not append an empty `## Phase N: Convergence` section.
- Update `Status` in `spec.md`'s document-control table to `Converged` and set today's date.
- Report: "Converged — the implementation satisfies the spec, plan, and constitution."
