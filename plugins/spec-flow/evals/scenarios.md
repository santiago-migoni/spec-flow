# Harness acceptance scenarios

Run each scenario in a disposable repository with a complete canonical release. Record the installed package revision, host/model evidence, commands, actual outcomes, and limitations. Unit fixtures that print a success string test orchestration mechanics only; the native end-to-end evaluation must implement and test an actual behavior.

| ID | Scenario | Required observable result |
| --- | --- | --- |
| EV-01 | New project with missing approvals | Gate reports exact missing decision; no implementation task starts. |
| EV-02 | Approved release with an executable behavioral test | Sol delegates a packet to Luna; actual behavior passes; Sol reviews; registry closes task once. |
| EV-03 | Legacy Approved tables and checked boxes | New execution refuses; explicit one-to-one migration preserves provenance, not fabricated evidence. |
| EV-04 | Change to code after verification | Close refuses stale evidence and identifies required recheck. |
| EV-05 | Agent interruption after file write | Resume reconciles file/attempt; does not recreate or repeat the write blindly. |
| EV-06 | Duplicate close | One completion event, stable result on replay. |
| EV-07 | Repeated failed implementation | Initial attempt plus two correction rounds; fourth prepare refuses and escalates. |
| EV-08 | File outside task scope modified | Verification/acceptance refuses; no silent rollback or acceptance. |
| EV-09 | Tests selector executes no cases | Exit zero alone does not close task. |
| EV-10 | Missing/mismatched model capability | Execution blocks without substituting Sol for Luna. |
| EV-11 | Shared architecture must change | Agent routes decision to architecture; dependent task stops, no scope edit by implementer. |
| EV-12 | All technical tasks complete, outcome unmeasured | Converge/closure preserve outcome pending; no push, merge or publication occurs automatically. |
| EV-13 | Two controllers use same project/run | Second owner cannot reserve or overwrite active execution. |
| EV-14 | Corrupted/truncated event tail | Recovery reports corruption; never treats log as empty/new execution. |
| EV-15 | Canonical spec changed after approval | Approval becomes stale; downstream work requires explicit applicable approval. |

## Evidence categories

- Deterministic: runtime/hook integration tests against temporary repositories.
- Native Codex: actual Sol/Luna delegation with host identity, diff and test output.
- Skill behavior: read-only pressure scenarios scored against their requested actions, not keywords alone.
- Distribution: relocated package and clean discovery in an isolated host context.

Report categories separately. Passing one does not establish another. Cost comparison uses only available measured usage; unavailable token/cost data remains unavailable, not zero. A reference run must use equivalent acceptance and checks; differences in task difficulty cannot establish savings.
