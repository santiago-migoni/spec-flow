# Spec — E7-only disposable fixture

```spec-flow
{
  "schema_version": 1,
  "kind": "spec",
  "revision": "R00",
  "id": "SPEC-1.2.3",
  "depends_on": [
    {
      "path": ".specs/roadmap.md",
      "digest": "365ff1a6541f2310a587973bfff7714e355a4c29cf162d63749d2b561b3c6b91"
    },
    {
      "path": ".specs/architecture.md",
      "digest": "41b1e09a052bfc9417437d418154934c75983343f7f9693faf318ab62b53b8f5"
    },
    {
      "path": ".specs/structure.md",
      "digest": "c71b1a1a748d1132cecc2cdb1ef826a1abe65e01a2cb931df68538cde6fb2d07"
    }
  ],
  "stories": [
    {
      "id": "US-001",
      "title": "Strict release normalization",
      "description": "As an E7 evaluator, I need a deterministic strict normalizer so that release identifiers have one canonical form."
    }
  ],
  "acceptance": [
    {
      "id": "AC-001",
      "story": "US-001",
      "description": "A bare or v-prefixed ASCII numeric triple normalizes to one v-prefixed triple, preserving component digits including zero and arbitrarily large components."
    },
    {
      "id": "AC-002",
      "story": "US-001",
      "description": "Malformed strings, leading zeros, Unicode digits, whitespace, suffixes and incorrect segment counts raise ValueError; non-string inputs raise TypeError."
    }
  ],
  "status": "converged"
}
```

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
{"delivery_status":"branch_retained","external_side_effects":false,"impact_evidence":[],"impact_status":"pending","kind":"release-review","phase_commits":[{"phase_id":"PH-01","sha":"8aad07dac4e8004aa639e6c3e4917f19844e6004"}],"publication":false,"release":"v1.2.3","run_id":"299d9b51-1a9d-4f5a-92e3-4ff20e9c58bc","schema":"spec-flow.derived-release.v1","technical_status":"complete"}
<!-- spec-flow:generated:end -->
