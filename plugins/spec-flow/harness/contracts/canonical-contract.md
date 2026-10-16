# Canonical Spec-Flow document contract

Each controller-governed Markdown source document contains exactly one fenced `spec-flow` block with a JSON object. Backlog is independent plain Markdown; conversation reports have no contract. Keep decision prose outside the block. `depends_on` paths are relative to the consuming project's root and pair a document path with its SHA-256 decision-content digest. Use [shared operations](operations.md) for query safety, adoption, validation, approval recording, and revisions; owning skills retain their specific gates and semantic checks.

Every contract has `schema_version: 1`, a `kind` from `constitution`, `architecture`, `structure`, `infrastructure`, `roadmap`, `spec`, `plan`, or `tasks`, a `revision` starting at `R00` and matching `R` plus at least two digits, a stable nonempty `id`, and a `depends_on` array. Dependency objects have project-root-relative `path` and lowercase 64-character hexadecimal `digest` fields. `status` is optional workflow metadata; when present, use `draft`, `approved`, or `converged`. It is excluded from the decision digest.

A `spec` adds nonempty `stories` and `acceptance` arrays. Each story is `{ "id": "US-001", "title": "...", "description": "..." }`; each criterion is `{ "id": "AC-001", "story": "US-001", "description": "..." }`. The `story` reference must exist. Acceptance prose belongs in the JSON contract once; surrounding Markdown may add context without duplicating criterion descriptions. A `tasks` document adds a nonempty `tasks` array. Each task has a stable `T-...` `id`, `phase`, a known `story`, acceptance criterion IDs belonging to that story, task ID dependencies, a nonempty `files` array, a nonempty ordered `steps` array, and a nonempty `closure`. Each step has a stable ID, an `action`, and a `verification` object containing exactly one of a nonempty argv `command` array or a specific `inspection` string, plus an `expected` result. Task IDs and step IDs are unique; task dependencies must exist and form an acyclic graph. Task file paths are relative to the project root, name individual files explicitly, and cannot target `.specs/`, `.spec-flow/`, or `.git/` metadata.

## Roadmap releases

A `roadmap` adds a nonempty `releases` array. Each entry has `version` (strict numeric `vX.Y.Z`, without leading zeros), a nonempty `objective`, and `status` from `planned`, `active`, `completed`, `deferred`, or `cancelled`. Versions are unique. The array owns release order and definitions; the [roadmap template](../../skills/roadmap/assets/roadmap-template.md) defines its synchronized reading table and explicit human selection. A `planned` entry alone does not prove that selection. Current release validation requires the version's canonical status to remain `planned`; selection does not set it to `active`. These nested release statuses are decisions included in the digest, unlike the optional top-level document status.

## Plan phases

A `plan` adds a nonempty `phases` array. Each entry has a unique `id` matching `PH-` plus at least two digits, a nonempty `description`, and `depends_on` containing known phase IDs (empty when none). References cannot be duplicated and the graph must be acyclic. This nested field references phase IDs, unlike document-level `depends_on`, which pins paths and digests. The array owns phase order/definitions; the [plan template](../../skills/plan/assets/plan-template.md) defines its synchronized reading table. Release tasks reference declared phases. The owning plan/tasks skills also review executable combined ordering and meaningful coverage; a valid graph does not prove feasibility.

The [document schema](../schemas/document.schema.json) describes field shapes; the runtime additionally validates references, digests, graphs, and full-release AC ownership/coverage. These definitions document existing requirements without adding fields or gates.

## Example: spec

```spec-flow
{
  "schema_version": 1,
  "kind": "spec",
  "revision": "R00",
  "id": "SPEC-1.2.3",
  "depends_on": [
    {"path": ".specs/roadmap.md", "digest": "<64 lowercase hex characters>"}
  ],
  "stories": [
    {"id": "US-001", "title": "Complete behavior", "description": "The user needs to complete the behavior."}
  ],
  "acceptance": [
    {"id": "AC-001", "story": "US-001", "description": "A user can complete the intended behavior."}
  ]
}
```

## Example: tasks

```spec-flow
{
  "schema_version": 1,
  "kind": "tasks",
  "revision": "R00",
  "id": "TASKS-1.2.3",
  "depends_on": [
    {"path": ".specs/release-v1.2.3/plan.md", "digest": "<64 lowercase hex characters>"}
  ],
  "tasks": [
    {
      "id": "T-001",
      "phase": "PH-01",
      "story": "US-001",
      "acceptance": ["AC-001"],
      "depends_on": [],
      "files": ["src/example.py"],
      "steps": [
        {
          "id": "T-001.001",
          "action": "Implement the behavior.",
          "verification": {
            "command": ["python3", "-m", "unittest"],
            "expected": "All relevant tests pass."
          }
        }
      ],
      "closure": "The behavior is implemented and its verification passes."
    }
  ]
}
```

A contract block must contain valid JSON. Documents must also contain nonempty decision prose without unresolved placeholder markers. Progress views may be placed in one explicit generated block after all decision prose and the contract:

```markdown
<!-- spec-flow:generated:start -->
Progress view maintained by the harness.
<!-- spec-flow:generated:end -->
```

Only that trailing delimited block and the top-level contract `status` field are excluded from `document_digest`; all other prose and contract decisions affect dependency digests. Generated markers cannot wrap or precede the contract, and generated content cannot replace the document's decision prose.
