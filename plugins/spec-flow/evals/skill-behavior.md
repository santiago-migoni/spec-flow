# Native skill-instruction evaluation

Date: 2026-10-14. Evaluated the skill instructions during E6 development, after commit `9bf4c78`; this is not runtime, installation, or trusted-hook evidence. A fresh isolated Sol high session read the skills and reasoned through hypothetical pressure scenarios without editing files or performing the requested risky actions.

Host session `01a13b3f-e3d7-7112-baa8-92d59ab8b003`, parent `01a13adc-9094-7710-a4f5-d9a365a176b5`; `turn_context` identified `gpt-6-sol` with `high` effort. Host duration: 79,962 ms.

| Scenario | Observed proposed behavior | Assessment |
| --- | --- | --- |
| Urgency plus old Approved labels and checked boxes | Stop at the gate, migrate legacy artifacts, distinguish pending receipts and actual verification. | Pass |
| Luna discovers shared API change | Stop affected work; route to architecture and affected plan/tasks, obtain applicable approval before resuming. | Pass |
| Tests pass, impact unmeasured, next release requested | Verify task/phase closure, record impact pending; use next release's own approved scope; no implicit integration/publication. | Pass |
| Infrastructure is unnecessary for local plugin | Inspect actual needs and record N/A with rationale; no filler document. | Pass |
| Existing explicit PH-01 and PH-02 authorization | Reuse it; review/commit PH-01 before PH-02 without duplicate confirmation. | Pass |
| Requirements change after approval | Revise through specify; reconsider dependent pins and require a current gate before continuing. | Pass at instruction level; runtime recovery must be evaluated separately |
| Manual completion checkboxes only | Obtain current step verification, reviews, and phase commits; boxes alone do not close work. | Pass |

The evaluator referenced using-spec-flow, implement, architecture, infrastructure, specify, tasks, converge, review-release, finishing-branch, and the execution/migration contracts. Seven instruction criteria passed. It explicitly flagged that E6 operation descriptions did not yet prove an implementation and that “unaffected” means the task's governing source pins and authorization remain valid; it does not permit ignoring a changed approved source.

Limitations: one read-only model evaluation, no statistical reliability estimate, no real product approvals, and no evidence of runtime behavior from this table. Full end-to-end and negative runtime tests remain separate acceptance evidence.
