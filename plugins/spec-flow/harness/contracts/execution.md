# Execution and delegation contract

This contract describes the implemented deterministic controller integration with native Codex agents. It does not claim Python can call model tools. The host-side Sol orchestrator checks available native capabilities, performs delegation, and supplies references; the controller validates records and state. Production CLI uses real host attestation and requires execution in an isolated linked Git worktree. Mechanics tests may inject `Engine(root, adapter=FakeAdapter)` through the library constructor; they must be labelled as such. There is no CLI environment switch that bypasses host checks.

## Profiles and authority

| Role | Required host profile | Authority |
| --- | --- | --- |
| Orchestrator | Sol high | Own run, select authorized tasks, inspect result, request corrections |
| Implementer | Luna high | Edit one scoped task and report results |
| Reviewer | Separate Sol high session | Assess integrated phase diff and evidence |
| Controller | Deterministic local runtime | Enforce approvals, transitions, verification, and evidence |

The user approves source decisions and authorizes execution scope. An existing authorization remains usable for its exact approved release and phases; a new phase or changed source needs appropriate authorization. No role may approve on the user's behalf. Execution approval does not include push, merge, publication, or deployment.

## Target controller operations

The CLI shape is `python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>`. These are the implemented E5 controller operations.

| Operation | Contract |
| --- | --- |
| capabilities | Validate host-supplied native operation/inventory references and attest the actual Sol owner session locally; Python does not enumerate or prove native tool availability |
| start / authorize | Bind attested Sol owner, approved release digests, explicit phase scope, and existing human authorization |
| prepare | Select one ready task and persist one immutable, bounded packet with source digests and file scope |
| bind-agent | Bind the canonical native agent path/ID, session ID, packet hash marker, model/effort, parent, and attempt from actual local host records; the ID must equal the host-recorded `agent_path` |
| result | Record the child's structured summary, changed files, checks, evidence, blockers, and hashed host attestation; compare changed paths to the real baseline |
| verify | Execute checks or capture specific inspection evidence against the real worktree and code fingerprint |
| review | Record Sol's task review against current verification; phase-end independent review remains E6 |
| close | Require current verification and task review, then close the task idempotently |
| interrupt / resume / reconcile | Rebuild state from events and inspect native agent/worktree state before any retry |
| takeover | For an interrupted run only, inspect old owner and child terminal records, persist the human-supplied reconciliation, and transfer the common-directory lease without changing approved phases; retries recover a lease transferred before its event was appended |
| retry | Permit a changed attempt with reason and hypothesis, at most three attempts total |
| status | Return the current run and active task without altering evidence |

The CLI accepts `capabilities` input `{"owner":"<session-id>","report":{"inventory_reference":"<host ref>","operations":{"spawn_agent":true,"wait_agent":true,"interrupt_agent":true,"list_agents":true},"probe_evidence":{"spawn_agent":"<ref>","wait_agent":"<ref>","interrupt_agent":"<ref>","list_agents":"<ref>"}}}`. Probe and inventory references are host-supplied; runtime checks their presence and validates the owner log. Task packets expose `packet_sha256`; include the exact marker `SPEC_FLOW_PACKET_SHA256=<hash>` in a delegated user prompt (markers in agent output do not attest delegation). Phase review, phase readiness, phase commits, and release review are E6 operations and are not implemented by this E5 controller.

The packet includes only the selected task, phase dependencies, selected acceptance criteria, applicable technical decisions, exact source digests, expected checks, and allowed files. If essential context cannot fit the configured size bound, return a diagnostic; never truncate a governing rule silently. Allowed files must be explicit file paths; directory scopes are rejected so scope checks and fingerprints use the same paths. A packet written before its event on a crash is reused after hash validation; changing `created_at` or repeating a side effect is not recovery.

## Evidence and stopping rules

The adapter verifies actual host session metadata and every turn context for model and reasoning effort. It also verifies native parent lineage, that the bound agent ID equals its host-recorded canonical agent path, packet markers in delegated user prompts, and a distinct reviewer session. Missing or mismatched evidence blocks the transition. The controller checks approved source digests, changed file scope, nonempty executed verification, and code fingerprint independently of the agent's report. An empty suite or test output from another revision cannot close a task.

One Luna is active per run. Sol reviews each task result; an independent Sol reviews the integrated phase at its boundary. Failures get a concrete hypothesis and targeted check. After three attempts, stop and escalate the unresolved issue. When a run is interrupted, inspect whether the original native agent is still active and reconcile its actual changes before retrying. A lost final message alone cannot justify replay.

A production run starts only in a linked Git worktree and uses one persistent active-controller registration in its common Git directory across worktrees. The lock protects atomic registration updates; the active record persists between calls. A worktree-local lock is insufficient. Initialization, strategy documents, and migration preview do not require a linked worktree. If ownership is ambiguous, stop for reconciliation rather than permitting two controllers.

Host logs and local registries are operational evidence, not cryptographic proof or an independent security boundary. The runtime detects scope breaches after writes; host permissions and isolated worktrees provide prevention.

## Phase commits and durable audit

Before a phase commit, all phase tasks must be closed with current verification, and a distinct attested Sol reviewer must approve the stable staged diff. Pin its expected parent and staged-tree digest. The Conventional Commit must match that reviewed tree. Append a compact phase-commit receipt with the SHA and review/evidence references after the commit; it may remain as the only pending audit change until the next phase includes it. A final audit-housekeeping commit captures the last receipt without generating another receipt. Keep compact events and durable evidence tracked; generated state, packets, and bulky logs may be ignored. A pending audit-only receipt does not count as unreviewed implementation, but any other post-review change invalidates the review. Next-phase authorization requires the prior phase's commit receipt and ancestry check.
