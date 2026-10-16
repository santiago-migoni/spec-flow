# E7 existing JSON candidate

```spec-flow
{
  "schema_version": 1,
  "kind": "architecture",
  "revision": "R00",
  "id": "ARCH-E7",
  "depends_on": [
    {
      "path": ".specs/constitution.md",
      "digest": "c8361c19642a1a5426539affda7f39d63df724dfcc0b292635dfee4880adcd64"
    }
  ]
}
```

# Architecture — E7-only disposable fixture

## Purpose, audience, and scope
E7 evaluators use this local module design for a disposable strict-normalization fixture.
## System context and boundaries
The caller passes a Python value to release.normalize_release; no process, network, persistent data, or external service participates.
## Current evidence and intended design
The verified starting release.py stub raises NotImplementedError. The fixed four-method test file specifies valid and invalid behavior. Intended design places exact normalization in release.py.
## Quality goals and constraints
Use Python stdlib only. Full-string ASCII matching and unchanged fixed tests are mandatory; four methods must pass.
| Attribute | Scenario | Expected result | Verification approach |
| --- | --- | --- | --- |
| Functional correctness | Exact ASCII triples or malformed/nonstring input | Normalize accepted digits; exact ValueError/TypeError for rejected values | Fixed four-method unittest suite |
| Integrity | Verification after implementation | release.py bytes remain unchanged during checks; test file is immutable | Hashes before/after and Git diff |
## Solution strategy
Implement one pure function with a compiled strict pattern or equivalent checks, preserving input component digits.
## Components, responsibilities, and contracts
release.py exports normalize_release(value). It returns a v-prefixed triple for accepted strings, raises TypeError for nonstrings and ValueError for malformed strings. test_release.py is the immutable verification client.
| ID | Component | Responsibility | Interfaces | Dependencies |
| --- | --- | --- | --- | --- |
| ARC-01 | release.py | Pure strict normalization | normalize_release(value) with exact return/error contract | Python stdlib only |
| ARC-02 | test_release.py | Fixed verification client, read-only | Four unittest methods | ARC-01 |
## Data and runtime scenarios
No stored data. Valid inputs include 1.2.3, v1.2.3, zero, huge components; invalid inputs include leading zero, Unicode digits, suffix and whitespace.
## Crosscutting concepts
N/A for auth, logging, transactions and distributed concerns because this is one local pure function. Error classes are part of the public contract.
## Decisions and consequences
Single-module stdlib implementation keeps verification deterministic and inspection bounded. This fixture decision does not extend plugin runtime design.
## Risks, technical debt, and open questions
The main risk is a permissive regex accepting Unicode digits, leading zeros, or trailing newline. Fixed tests expose these cases. No blocking open question.
## References and amendment history
Synthetic E7-only decision, sourced to the fixed test file and approved fixture constitution. R00 initial version.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
