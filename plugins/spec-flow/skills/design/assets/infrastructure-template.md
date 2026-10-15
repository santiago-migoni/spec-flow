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
    }
  ]
}
```

Replace the example constitution digest with its approved digest. Add exact-digest dependencies only for approved strategic documents whose decisions are actually used. Recommended elaboration order: architecture → infrastructure → structure; this is not a mandatory dependency chain. If a whole document is inapplicable, record N/A with a reason in the roadmap under its own gate. Omitting a dependency alone does not make its document N/A. Do not create filler or future dependent documents to complete this one; keep dependency pins acyclic and navigational links separate.

## Purpose, audience, and operational scope

[Identify readers and relevant execution modes: local runtime/host, services, cloud, or others. Explain N/A for sections that do not apply; a local plugin does not imply hosted infrastructure.]

## Current state and evidence

[Distinguish declared configuration, tested behavior, deployed resources, and pending proposals. Cite evidence; approved design does not prove deployment or successful operation.]

## Environments and resources

| Environment | Platform or resource | Purpose | Owner | State and evidence |
| --- | --- | --- | --- | --- |
| [Name] | [Resource] | [Use] | [Role or person] | [Verified or proposed; reference] |

## Deployment mapping and connections

[Map component IDs to execution resources, connections, and external dependencies. Use a deployment diagram when useful and explain the choices. Link repository locations once defined; structure is not a default prerequisite.]

## Configuration, access, and secrets

[Describe configuration per environment, permission boundaries, and secret management mechanisms. Reference secure locations without including secret values.]

## Build, distribution, deployment, and rollback

[Describe the strategy, verification requirements, and rollback conditions. Link automation and detailed procedures. Mark untested procedures as proposed; documenting them does not authorize execution.]

## Observability and operations

| Signal or condition | Objective or threshold | Response | Owner | Procedure |
| --- | --- | --- | --- | --- |
| [Metric, log, or condition] | [Agreed value or pending] | [Action] | [Role or person] | [Reference or pending] |

## Capacity, limits, and costs

[Record needs, load assumptions, limits, and relevant estimates. Separate estimates from current measurements; do not invent commitments or operational targets.]

## Backup, restoration, and recovery

[Identify data/state requiring protection and recovery objectives when applicable: RTO for restoration time, RPO for tolerable data loss. Reference recovery procedures and test evidence; distinguish planned tests from completed results.]

## Decisions, risks, and operational questions

[For significant choices record ID, context, alternatives, decision, rationale, consequences, and review conditions, or link existing ADRs. Record risks, assumptions to validate, and unresolved human decisions.]

## References and amendment history

[Link configuration, automation, procedures, approved decisions, and scoped operational evidence. Record approved revisions and reasons. Revisit when environments, resources, deployment, access, or recovery decisions change.]

<!-- spec-flow:generated:start -->
Progress is maintained by the Spec-Flow harness.
<!-- spec-flow:generated:end -->
