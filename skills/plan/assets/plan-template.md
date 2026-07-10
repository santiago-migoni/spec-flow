---
name: [short-description]
code: PLAN-NNN
version: R00
date: [YYYY-MM-DD]
---

# Plan: [Feature Name]

## Approach

[2-3 sentences: the chosen implementation strategy and why]

## Constitution Check

- **Tech stack**: [Confirm alignment with constitution or flag conflict]
- **Code principles**: [List any principle specifically relevant to this feature]
- **Constraints**: [Any constitution constraint that shapes this plan]

## Architecture

[Describe the architecture. Keep it to what matters for this feature — don't redesign the whole system.]

## File Structure

```text
[Exact paths of files that will be created or modified]
src/
├── new-file.ts          ← [what it contains]
└── modified-file.ts     ← [what changes]
```

## Data Model

[If applicable: entities, fields, relationships. If not applicable, write "N/A".]

## API / Interface Contracts

[If applicable: function signatures, endpoint contracts, CLI interface. If not applicable, write "N/A".]

## Dependencies

[New packages or tools required. If none, write "None — existing dependencies suffice".]

## Risks & Unknowns

- [Risk 1 and mitigation]
- [NEEDS CLARIFICATION: anything that can't be decided until implementation starts]
