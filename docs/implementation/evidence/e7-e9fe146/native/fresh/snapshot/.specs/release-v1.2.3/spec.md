---
schema_version: 1
kind: spec
revision: R00
id: SPEC-1.2.3
depends_on:
- path: .specs/roadmap.md
  digest: 4cc8ed79a7d7b76b0a176a7c1a224a0d8eb0642288b8c8f95d75b58302f52c4f
- path: .specs/architecture.md
  digest: 59647883742a62fc9d7621cb8737a3c57ca3e54f73a11c60f97aa0d56588d885
- path: .specs/structure.md
  digest: 984231f958e73bea68ed983b70bd0de6f845125428728cc21bde6708d540a8dd
stories:
- id: US-001
  title: Strict release normalization
  description: As an E7 evaluator, I need a deterministic strict normalizer so that release identifiers
    have one canonical form.
acceptance:
- id: AC-001
  story: US-001
  description: A bare or v-prefixed ASCII numeric triple normalizes to one v-prefixed triple, preserving
    component digits including zero and arbitrarily large components.
- id: AC-002
  story: US-001
  description: Malformed strings, leading zeros, Unicode digits, whitespace, suffixes and incorrect segment
    counts raise ValueError; non-string inputs raise TypeError.
status: converged
---

# Spec — E7-only disposable fixture

## Purpose and selected release
The approved roadmap explicitly selects v1.2.3 for the E7 fixture.
## Users, context, and expected outcome
The evaluator calls normalize_release from local Python; OUT-001 is demonstrated by four fixed tests.
## Scope and exclusions
Implement release.py only. No CLI, packaging, deployment, or test editing.
## Approved bases and constraints
Constitution MUST rules, architecture interface, and structure paths apply. Infrastructure is N/A for this local function.
## User stories
| Story | Related outcomes | Acceptance criteria | Relevant dependencies |
| --- | --- | --- | --- |
| US-001 | OUT-001 | AC-001, AC-002 | Fixed suite |
## Rules, acceptance, and examples
| Criterion | Situation or input | Action or event | Expected result |
| --- | --- | --- | --- |
| AC-001 | `1.2.3`, `v1.2.3`, `0.0.0`, huge ASCII integers | normalize_release | Exact v-prefixed triple |
| AC-002 | `01.2.3`, `1.2.٣`, whitespace, suffix, None | normalize_release | ValueError for strings; TypeError for nonstrings |
## Quality and conditions of done
| ID | Attribute | Conditions | Result or threshold | Verification approach | Related criteria |
| --- | --- | --- | --- | --- | --- |
| NFR-001 | Deterministic strictness | All fixed samples | Four unittest methods pass; test file unchanged | `python3 -B -m unittest -v test_release.py` | AC-001, AC-002 |
## Edge cases, errors, and compatibility
AC-002 includes Python bool as nonstring despite its int subclass. No permissive whitespace stripping.
## Post-delivery measurement
Run evidence shows technical behavior. Real-world impact is pending and out of scope.
## Assumptions, dependencies, and open questions
No blocking question; stdlib Python and fixed test file are present.
## Readiness for planning, approval, and amendments
All observable behavior and error classes are in canonical ACs; this is an E7-only fixture approval.

<!-- spec-flow:generated:start -->
Spec-Flow derived record:
{"delivery_status":"branch_retained","external_side_effects":false,"impact_evidence":["Synthetic E7 fixture technical suite only; no external users or observed impact."],"impact_status":"pending","kind":"release-review","phase_commits":[{"phase_id":"PH-01","sha":"48a248943c3e0c12bccb9fa88cb303476e6c95d3"}],"publication":false,"release":"v1.2.3","run_id":"8a974b4c-ef05-4e2c-b323-6a8899b93552","schema":"spec-flow.derived-release.v1","technical_status":"complete"}
<!-- spec-flow:generated:end -->
