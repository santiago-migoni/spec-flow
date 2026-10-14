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

The CLI shape is `python3 <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>`. These are the implemented controller operations. The production adapter validates and persists host records; it never launches model APIs or tools itself.

| Operation | Contract |
| --- | --- |
| capabilities | Validate host-supplied native operation/inventory references and attest the actual Sol owner session locally; Python does not enumerate or prove native tool availability |
| start / authorize | Bind attested Sol owner, approved release digests, explicit phase scope, and existing human authorization |
| prepare | Select one ready task and persist one immutable, bounded packet with source digests and file scope |
| restore-packet | Restore a missing task or phase packet cache only when current approved pins reproduce the event-recorded hash; preserves attempts and agent bindings and refuses corrupt caches |
| bind-agent | Bind the canonical native agent path/ID, session ID, packet hash marker, model/effort, parent, and attempt from actual local host records; the ID must equal the host-recorded `agent_path` |
| result | Record the child's structured summary, changed files, checks, evidence, blockers, and hashed host attestation; compare changed paths to the real baseline |
| verify | Execute checks or capture specific inspection evidence against the real worktree and code fingerprint |
| review | Record Sol's task review against current verification |
| close | Require current verification and task review, then close the task idempotently |
| interrupt / resume / reconcile | Rebuild state from events and inspect native agent/worktree state before any retry; `no_spawn` requires a fresh owner-scoped `list_agents` inventory, packet-marker checks against local child logs, and unchanged task files |
| takeover | For an interrupted run only, inspect old owner and child terminal records, persist the human-supplied reconciliation, and transfer the common-directory lease without changing approved phases; retries recover a lease transferred before its event was appended |
| abandon | After reconciling any active task, record a reason and explicit authorization, preserve the old event history, and release ownership idempotently so a new run can use current approved pins |
| retry | Permit a changed attempt with reason and hypothesis, at most three attempts total |
| status | Return the current run and active task without altering evidence |
| phase-ready | Validate current approvals, completed task evidence, scope, and idle state; stage exact phase/audit paths and pin HEAD, tree, and diff hashes |
| review-phase | Require an independent completed Sol high review attested to the exact run/phase/tree marker |
| commit-phase | Revalidate the pin, write the Conventional Commit and durable compact phase receipt; recovery adopts only one exact commit on current HEAD ancestry |
| refresh-evidence | Rerun current checks for a completed task when relevant code changed; does not repeat implementation or task credit |
| release-review | Write derived release/roadmap records, capture final receipts and events in one audit-only commit, then release the owner lease |
| complete | Read-only technical completion query for current source pins, task evidence, and phase commit ancestry; also reports pending release review/audit closure |
| hook-check | Read-only shared-engine authorization and scope validation for supported local `apply_patch`, `Edit`, and `Write` path inputs |

For cache loss, call `restore-packet` with `{"run_id":"<run-id>","owner":"<sol-session-id>","kind":"task","task_id":"T-001"}` or `{"run_id":"<run-id>","owner":"<sol-session-id>","kind":"phase","phase_id":"PH-01"}`. It does not create attempts, delegate agents, or mutate source code. Restoration requires the active controller lease, current owner attestation, current approved source pins, and an exact match to the recorded packet hash. Existing corrupt files are never overwritten. If an older event did not persist the original packet creation timestamp, restoration fails with `packet_timestamp_unavailable` rather than inventing one.

The CLI accepts `capabilities` input `{"owner":"<session-id>","report":{"inventory_reference":"<host ref>","operations":{"spawn_agent":true,"wait_agent":true,"interrupt_agent":true,"list_agents":true},"probe_evidence":{"spawn_agent":"<ref>","wait_agent":"<ref>","interrupt_agent":"<ref>","list_agents":"<ref>"}}}`. Probe and inventory references are host-supplied; runtime checks their presence and validates the owner log. Python cannot enumerate native tools or independently prove the supplied probe references. `prepare` returns `packet_sha256` and `native_task_name`. Include `SPEC_FLOW_PACKET_SHA256=<packet_sha256>` in the Luna prompt and pass the returned name as `spawn_agent.task_name`; it is `luna_` plus lowercase SHA-256 of the complete marker. `phase-ready` similarly returns `phase_marker` and `native_task_name`, where the name is `review_` plus lowercase SHA-256 of the complete `SPEC_FLOW_PHASE_REVIEW=<run>/<phase>/<tree>` marker. The adapter accepts a visible exact marker in the child user prompt, or—when the host encrypts that prompt—a parent-log `collaboration.spawn_agent` call with the hash-bearing task name, its call-ID-linked output containing the child path, and matching child parent/path lineage. It records hashes of the native call and output; encrypted prompt contents are not claimed as inspected. Assistant prose/output never attests delegation. No-spawn reconciliation fails closed when a child created during the attempt cannot be attributed.

Concrete phase calls use the normal `--input` JSON-file interface. For `phase-ready`, `review-phase`, or `commit-phase`, begin with `{"run_id":"<run-id>","owner":"<sol-session-id>","phase_id":"PH-01"}`. `phase-ready` returns a bounded packet and marker tied to the exact pinned tree. The independent Sol reviewer receives that packet and exact marker in its delegated user prompt. `review-phase` then takes those fields plus `reviewer_session`, `reviewer_agent_id` (canonical native agent path), `verdict` (`pass` or `changes`), and nonempty `evidence`. A passing review is followed by `commit-phase` with those three identifiers and a Conventional Commit `subject`, such as `feat(search): add scoped filters`.

After every declared phase has committed, `complete` reports technical completion and whether release review/audit closure is pending. Then call `release-review` with `run_id`, `owner`, `impact_status` (`observed`, `pending`, or `unavailable`), `impact_evidence` (durable references; required when observed), and optional `delivery_status` (`branch_committed`, `branch_retained`, or `not_integrated`). The derived record always keeps `publication: false` and `external_side_effects: false`; this writes the final audit commit and releases the owner lease. `complete` accepts `{"release":"vX.Y.Z"}` and optionally `run_id`; it reads only. `scripts/check-complete.sh <canonical tasks.md>` checks technical completion and maps complete to exit 0, incomplete to exit 1, and invalid input/runtime error to exit 2.

`abandon` accepts `{"run_id":"<run-id>","owner":"<sol-session-id>","reason":"Approved sources changed.","authorization":{"actor":"user","statement":"Abandon the stale run and preserve its history.","source":"conversation"}}`. It refuses while a task attempt remains active; resume and reconcile the native child first. Repeating the operation after a crash completes any pending lease release without duplicating the abandonment event. If `prepare` persisted before native spawn, first resume the run and reconcile with `disposition: "no_spawn"` only after current owner-scoped host inventory and packet-marker inspection confirms there is no task child and the attempt baseline is unchanged. The input uses `native_inspection: {"owner_session":"<sol-session-id>","inventory_reference":"<list_agents result ref>","checked_at":"<UTC timestamp>","agents":[{"agent_path":"<native path>","status":"completed"}]}`; use an empty `agents` list when the host reports no agents. A matching child prompt marker blocks this disposition and must be late-bound and reconciled normally. `close` completes one task only; it does not complete the run or release cross-worktree ownership. The lease remains active through final release review and is released after the audit commit. The `PreToolUse` hook delegates supported path checks to shared-engine `hook-check`. It does not claim coverage for shell commands, arbitrary tools, every write path, or a hostile host; malformed supported write inputs are denied.

The packet includes only the selected task, phase dependencies, selected acceptance criteria, applicable technical decisions, exact source digests, expected checks, and allowed files. If essential context cannot fit the configured size bound, return a diagnostic; never truncate a governing rule silently. Allowed files must be explicit file paths; directory scopes are rejected so scope checks and fingerprints use the same paths. A packet written before its event on a crash is reused after hash validation; changing `created_at` or repeating a side effect is not recovery.

## Evidence and stopping rules

The adapter verifies actual host session metadata and every turn context for model and reasoning effort. It also verifies native parent lineage, that the bound agent ID equals its host-recorded canonical agent path, packet markers in delegated user prompts, and a distinct reviewer session. Missing or mismatched evidence blocks the transition. The controller checks approved source digests, changed file scope, nonempty executed verification, and code fingerprint independently of the agent's report. An empty suite or test output from another revision cannot close a task.

One Luna is active per run. Sol reviews each task result; an independent Sol reviews the integrated phase at its boundary. Failures get a concrete hypothesis and targeted check. After three attempts, stop and escalate the unresolved issue. When a run is interrupted, inspect whether the original native agent is still active and reconcile its actual changes before retrying. A lost final message alone cannot justify replay.

A production run starts only in a linked Git worktree and uses one persistent active-controller registration in its common Git directory across worktrees. The lock protects atomic registration updates; the active record persists between calls. A worktree-local lock is insufficient. Initialization, strategy documents, and migration preview do not require a linked worktree. If ownership is ambiguous, stop for reconciliation rather than permitting two controllers.

Host logs and local registries are operational evidence, not cryptographic proof or an independent security boundary. The runtime detects scope breaches after writes; host permissions and isolated worktrees provide prevention.

## Phase commits and durable audit

Before a phase commit, all phase tasks must be closed with current verification, and a distinct attested Sol reviewer must approve the stable staged diff. Pin its expected parent and staged-tree digest. The Conventional Commit must match that reviewed tree. Append a compact phase-commit receipt with the SHA and review/evidence references after the commit; it may remain as the only pending audit change until the next phase includes it. `release-review` creates one final audit-only commit that captures the last receipt, derived docs, and release-review event without generating another receipt. Keep compact events and durable evidence tracked; generated state and bounded packets may be ignored. Any post-review implementation change invalidates the review. Next-phase preparation requires prior phase commits in current branch ancestry.
