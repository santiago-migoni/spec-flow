# Release Tasks: vX.Y.Z

```spec-flow
{
  "schema_version": 1,
  "kind": "tasks",
  "revision": "R00",
  "id": "TASKS-X.Y.Z",
  "depends_on": [
    {
      "path": ".specs/release-vX.Y.Z/plan.md",
      "digest": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ],
  "tasks": [
    {
      "id": "T-001",
      "phase": "PH-01",
      "story": "US-001",
      "acceptance": [
        "AC-001"
      ],
      "depends_on": [],
      "files": [
        "src/example.py",
        "tests/test_example.py"
      ],
      "steps": [
        {
          "id": "T-001.001",
          "action": "[Implement and test the enabling change contributing partially to AC-001 in the listed files.]",
          "verification": {
            "command": [
              "python3",
              "-B",
              "-m",
              "unittest",
              "discover",
              "-s",
              "tests",
              "-p",
              "test_example.py",
              "-k",
              "enabling"
            ],
            "expected": "[Enabling cases execute and pass; contribution to AC-001 remains partial.]"
          }
        }
      ],
      "closure": "[Enabling change verified; AC-001 contribution remains partial.]"
    },
    {
      "id": "T-002",
      "phase": "PH-01",
      "story": "US-001",
      "acceptance": ["AC-001", "AC-002", "AC-003"],
      "depends_on": ["T-001"],
      "files": ["src/example.py", "tests/test_example.py", "tests/test_quality.py"],
      "steps": [
        {
          "id": "T-002.001",
          "action": "[Complete the successful behavior of AC-001 and its final acceptance check.]",
          "verification": {
            "command": ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_example.py", "-k", "success"],
            "expected": "[Executed success cases demonstrate the complete behavior required by AC-001.]"
          }
        },
        {
          "id": "T-002.002",
          "action": "[Complete the relevant invalid-input or failure behavior of AC-002 and its final acceptance check.]",
          "verification": {
            "command": ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_example.py", "-k", "invalid"],
            "expected": "[Executed error cases demonstrate the response required by AC-002.]"
          }
        },
        {
          "id": "T-002.003",
          "action": "[Meet the NFR-001 conditions and target referenced by AC-003 and add its quality check.]",
          "verification": {
            "command": ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_quality.py"],
            "expected": "[Executed quality checks satisfy NFR-001 under its approved conditions and demonstrate AC-003.]"
          }
        }
      ],
      "closure": "[US-001 complete with final verification of AC-001, AC-002, and AC-003.]"
    },
    {
      "id": "T-003",
      "phase": "PH-02",
      "story": "US-002",
      "acceptance": ["AC-004"],
      "depends_on": ["T-002"],
      "files": ["src/related.py", "tests/test_integration.py"],
      "steps": [
        {
          "id": "T-003.001",
          "action": "[Implement the related US-002 increment and integration behavior for AC-004 with its tests.]",
          "verification": {
            "command": ["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_integration.py"],
            "expected": "[Executed integration cases demonstrate AC-004 and relevant regression checks pass.]"
          }
        }
      ],
      "closure": "[US-002 complete with final verification of AC-004.]"
    }
  ]
}
```

Replace the illustrative tasks, references, paths, commands, selectors, and expected results with this release's actual decisions. Confirm that selected checks exist and exercise the intended behavior; these examples prescribe neither task count nor scope. The tasks array owns all executable task definitions. Keep reading tables synchronized and outside generated progress; their decision context participates in the document digest.

## Purpose and approved bases

[Identify the release, approved plan/spec bases, implementation objective, and applicable shared decisions. Reference approved definitions rather than repeating scope or acceptance. Resolve stale bases or conflicts before decomposition.]

## Decomposition criteria

[Explain the chosen granularity. Each task has a specific, measurable, achievable, relevant, bounded contribution that can be implemented, verified, and reviewed clearly. Justify enabling work; explain what it unlocks. Put relevant tests and checks alongside the change. Record any estimate's basis and uncertainty, using time as guidance rather than an automatic human-hours rule for agents.]

## Task map

This is a reading view of tasks. Include every task exactly once, in canonical order. Copy id, phase, story, acceptance IDs/order, depends_on IDs/order, and closure exactly; render an empty dependency list as None.

| Task | Phase | Story | Related criteria | Dependencies | Closure condition |
| --- | --- | --- | --- | --- | --- |
| T-001 | PH-01 | US-001 | AC-001 | None | [Enabling change verified; AC-001 contribution remains partial.] |
| T-002 | PH-01 | US-001 | AC-001, AC-002, AC-003 | T-001 | [US-001 complete with final verification of AC-001, AC-002, and AC-003.] |
| T-003 | PH-02 | US-002 | AC-004 | T-002 | [US-002 complete with final verification of AC-004.] |

## Sequence and dependencies

[Explain the actual prerequisites and ordering rationale, consistent with plan phases and their dependencies. Review both graphs together for an executable sequence, including dependencies that could block a phase on later work. Avoid artificial chains. Logical independence does not authorize parallel execution: retain one active implementer and independent phase review/commit.]

## File scope and restrictions

[Explain placement and scope decisions in relation to approved structure and the plan. Distinguish existing/proposed files. Each task's files array names individual contained project-relative files, including relevant tests. Protected .specs, .spec-flow, and .git metadata are excluded. Put task-specific operative restrictions in action/closure and files; background here cannot expand the current task's permitted writes. Dependency files can appear in context without becoming writable by the current task.]

## Acceptance and quality coverage

This matrix describes intended contributions and final checks, not completed acceptance. Every AC appears once in canonical spec order under its actual story owner. Include all contributing task IDs, label partial contributions, and identify existing final-verification step IDs whose tasks reference that AC.

| Criterion | Owning story | Contributing tasks | Final verification step | Quality reference |
| --- | --- | --- | --- | --- |
| AC-001 | US-001 | T-001: partial; T-002: complete | T-002.001 | None |
| AC-002 | US-001 | T-002 | T-002.002 | None |
| AC-003 | US-001 | T-002 | T-002.003 | NFR-001 |
| AC-004 | US-002 | T-003 | T-003.001 | None |

[Check coverage against spec and the plan's delivery/final-verification phases. A task's acceptance reference may represent only a partial contribution; nominal ID coverage alone does not establish final satisfaction. Reflect partial/final intent in canonical action, expected, and closure fields, not solely this table. Reference NFR conditions/targets from their approved definition. Map applicable constitution/shared-quality checks to actual task steps. Return missing acceptance or changed behavior to specify and changed technical decisions to plan or their shared owner.]

## Verification and evidence

Each canonical step has one action and exactly one verification method: an argv command list or a specific inspection, plus its expected result. Choose meaningful checks for the actual change, including relevant errors, quality, integration, and regression. For an inspection, specify the surface, conditions, and observable evidence to examine. Verification commands run from the project root against the resulting task state and must leave project code unchanged; implementation, generation, and migration actions belong in action, with separate checks. Passing commands, nonempty output, and current review evidence remain required; test suites must execute cases.

The task packet retains canonical task records and their transitive dependencies, but discards this document's prose and tables. Put every execution-critical instruction in files, action, verification, or closure, or an approved governing source actually retained in the scoped packet. Review that representation before approval without starting execution. A reference to omitted prose cannot supply missing instructions; context about future work is not authorization.

## Risks, blockers, and readiness

[Record remaining uncertainties, access/tools/environment needs, and blocking conditions. Resolve decisions affecting behavior or solution in their owning source. Any executable exploration needs a clear question, boundary, expected evidence, and stopping condition in canonical fields, with an honest story/AC contribution and explicit file scope. Return work that cannot fit that contract to plan rather than inventing stories, criteria, or task types.]

Before implementation, review current approved bases, executable tasks across all release phases, complete AC coverage with adequate final checks, coherent tables and phase/task graphs, valid file scope, usable checks, required context, and resolved blockers. These are readiness review requirements, not progress checkboxes. Validate tasks and the full release; approval and execution authorization remain distinct scopes.

## Closure and progress

[Explain how task closure contributes to criteria, phase review/commit, and release completion. A partial task can close without satisfying its whole AC. Close tasks through current verification and review evidence; phase and release closure retain their own controls. Planning an operational action does not authorize integration, publication, or deployment.]

Progress and checkboxes are generated from controller evidence. Keep decision tables out of generated progress and do not maintain a second manual status list. The controller validates structural contracts and nominal AC coverage; table coherence, semantic sufficiency, and feasibility require explicit skill review.

## Refinement, references, and approval

[Record references, actual revisions/approval scope, reasons for changes, and affected documents. Refine through approved revisions while preserving completed work, historical evidence, and stable IDs for unchanged tasks/steps; use new IDs for new work. Changed source decisions return to their owner, with affected pins inspected/adopted explicitly. Reconcile active execution before retrying; evidence and authorization are reused only while their contracts, sources, fingerprints, and scopes remain applicable.]

Full-release tasks and AC coverage remain required before execution. Later phases must be sufficiently defined; progressive elaboration does not authorize placeholders or first-phase-only coverage. The registry controls approval. One explicit human statement can approve tasks and authorize execution when it clearly covers both scopes; existing execution authorization is reusable within its approved scope.

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
