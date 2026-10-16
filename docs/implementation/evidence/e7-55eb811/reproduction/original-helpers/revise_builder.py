from pathlib import Path
p=Path('/private/tmp/spec-flow-e7-55eb811-nh63aagh/prepare_fresh.py')
s=p.read_text().replace("root=B/'fresh-main'","root=B/'faithful-main'")
a=s.index("architecture=doc(")
b=s.index("obj='Evaluate strict",a)
replacement='''architecture=doc('.specs/architecture.md','architecture','ARCH-E7',[constitution],{},\"\"\"## Purpose, audience, and scope
E7 evaluators use this local module design for a disposable strict-normalization fixture.
## System context and boundaries
The caller passes a Python value to release.normalize_release; no process, network, persistent data, or external service participates.
## Current evidence and intended design
The verified starting release.py stub raises NotImplementedError. The fixed four-method test file specifies valid and invalid behavior. Intended design places exact normalization in release.py.
## Quality goals and constraints
Use Python stdlib only. Full-string ASCII matching and unchanged fixed tests are mandatory; four methods must pass.
## Solution strategy
Implement one pure function with a compiled strict pattern or equivalent checks, preserving input component digits.
## Components, responsibilities, and contracts
release.py exports normalize_release(value). It returns a v-prefixed triple for accepted strings, raises TypeError for nonstrings and ValueError for malformed strings. test_release.py is the immutable verification client.
## Data and runtime scenarios
No stored data. Valid inputs include 1.2.3, v1.2.3, zero, huge components; invalid inputs include leading zero, Unicode digits, suffix and whitespace.
## Crosscutting concepts
N/A for auth, logging, transactions and distributed concerns because this is one local pure function. Error classes are part of the public contract.
## Decisions and consequences
Single-module stdlib implementation keeps verification deterministic and inspection bounded. This fixture decision does not extend plugin runtime design.
## Risks, technical debt, and open questions
The main risk is a permissive regex accepting Unicode digits, leading zeros, or trailing newline. Fixed tests expose these cases. No blocking open question.
## References and amendment history
Synthetic E7-only decision, sourced to the fixed test file and approved fixture constitution. R00 initial version.\"\"\")
structure=doc('.specs/structure.md','structure','STRUCT-E7',[constitution,architecture],{},\"\"\"## Purpose, audience, and scope
This E7-only file placement governs the local module fixture.
## Verified current organization
The verified starting tree has release.py (stub), test_release.py (fixed four-method suite), .specs/ (decisions), and .spec-flow/ (controller records after adoption).
## Architecture-to-repository mapping
The architecture's normalize_release contract maps to release.py; the immutable client and test evidence map to test_release.py.
## Intended organization and placement rules
Keep the same tree. Edit release.py only for implementation; controller owns .spec-flow and generated progress.
## Naming conventions and public interfaces
Export normalize_release exactly from release.py; no package rename or added entry point.
## Dependencies and module boundaries
Only Python stdlib may be imported. The test imports release; release must not import test_release.
## Tests, configuration, documentation, and resources
The fixed test_release.py is read-only. There is no runtime config or resource required for this pure function.
## Generated files, third parties, and distribution
The controller manages generated .spec-flow records; Python bytecode is ignored. No third-party package or distribution target.
## Decisions, risks, and pending structural changes
The permitted implementation scope is release.py. A changed path requires an approved tasks/structure revision; none is pending.
## References and amendment history
Synthetic E7-only R00 decision; initial tree inspected before approval.\"\")
'''
s=s[:a]+replacement+s[b:]
Path('/private/tmp/spec-flow-e7-55eb811-nh63aagh/prepare_faithful.py').write_text(s)
