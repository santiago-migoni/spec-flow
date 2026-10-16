---
schema_version: 1
kind: structure
revision: R00
id: STRUCT-PROJECT
depends_on:
- path: .specs/constitution.md
  digest: '0000000000000000000000000000000000000000000000000000000000000000'
---

# Code Structure

Replace the example constitution digest with its approved digest. Add exact-digest dependencies only for approved strategic documents whose decisions are actually used. Recommended elaboration order: architecture → infrastructure → structure; this is not a mandatory dependency chain. If a whole document is inapplicable, record N/A with a reason in the roadmap under its own gate. Omitting a dependency alone does not make its document N/A. Do not create filler or future dependent documents to complete this one; keep dependency pins acyclic and navigational links separate.

## Purpose, audience, and scope

[Define what readers should be able to locate, understand, or change using this document. Explain N/A for sections that do not apply.]

## Verified current organization

[Provide an annotated tree of important existing directories and files based on repository inspection. Set a useful depth and state omissions such as downloaded dependencies or repetitive generated content. Replace the illustrative tree below with verified paths; it does not prescribe a src/ layout.]

```text
project/
├── src/                 # Product source
├── tests/               # Tests
└── docs/                # Documentation
```

## Architecture-to-repository mapping

| Component or responsibility | Path | Current or proposed state | Entry point |
| --- | --- | --- | --- |
| [ARC-01 or known responsibility] | [relative/path] | [Verified or proposed] | [File or symbol] |

[Reference architectural responsibilities without duplicating them. Link infrastructure decisions that affect package or deployment layout when used.]

## Intended organization and placement rules

[If changes are proposed, include a separate annotated tree of the intended layout, clearly labeled as proposed. Do not mix future paths into the verified current tree. If no changes are needed, say so and omit the second tree.]

| Path or category | Contents | Placement rule | Restrictions |
| --- | --- | --- | --- |
| [relative/path or category] | [Purpose] | [Where a new element belongs and why] | [Boundary] |

## Naming conventions and public interfaces

[Define relevant naming conventions, entry points, and how public surfaces are identified.]

## Dependencies and module boundaries

[Describe allowed dependencies, restricted access, and available mechanisms to verify these rules. Reference component IDs rather than restating design.]

## Tests, configuration, documentation, and resources

[Specify their locations and relationship to components. Reference infrastructure's operational decisions instead of copying them.]

## Generated files, third parties, and distribution

[Identify editable sources, generated outputs, incorporated third-party content, and distributable artifacts. Link generation/distribution processes; omit their repetitive file details from the tree.]

## Decisions, risks, and pending structural changes

[Record significant organization decisions with ID, context, alternatives, choice, rationale, consequences, and review conditions, or link existing ADRs. Separate verified paths from proposals. Record risks, assumptions, and pending questions; implementation detail belongs in release plans.]

## References and amendment history

[Link source evidence and approved decisions actually used. Record approved revisions and reasons. Revisit when module layout, dependency rules, public entry points, or distribution boundaries change.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
