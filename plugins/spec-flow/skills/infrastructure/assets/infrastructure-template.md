# Infrastructure

```spec-flow
{
  "schema_version": 1,
  "kind": "infrastructure",
  "revision": "R00",
  "id": "INFRA-PROJECT",
  "depends_on": [
    {
      "path": ".specs/constitution.md",
      "digest": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "path": ".specs/architecture.md",
      "digest": "0000000000000000000000000000000000000000000000000000000000000000"
    },
    {
      "path": ".specs/structure.md",
      "digest": "0000000000000000000000000000000000000000000000000000000000000000"
    }
  ]
}
```

Replace example dependencies with only the approved strategic documents actually used. An omitted document is recorded as N/A with a reason in the roadmap; do not create an empty document.

## Current operational evidence

[Identify deployed behavior verified from the repository or environment.]

## Environments and resources

| Environment | Resources | Secrets boundary | Owner |
| --- | --- | --- | --- |
| [name] | [resources] | [handling] | [owner] |

## Deployment, rollback, and recovery

[State procedures and testable requirements.]

## Observability and operations

[State signals, alerts, and operating responsibilities.]

## Open questions

[Separate proposed operations from verified current behavior.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
