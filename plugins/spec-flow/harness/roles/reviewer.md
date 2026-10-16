# Independent reviewer role

A phase-end reviewer is a distinct attested session matching the run's pinned reviewer model and effort. It cannot be the implementer or the orchestrator session. Spawn it with isolated history (`fork_turns: "none"`) after the phase's implementation is stable.

Receive the approved phase scope/deliverables, relevant ACs and quality definitions, planned partial/final contributions, governing decisions, actual pinned diff, controller verification artifacts, source digests, and code fingerprint. Confirm the review corresponds to this exact run/phase/tree marker and returned native reviewer name under adapter attestation.

Inspect integrated behavior, relevant acceptance/error/quality/regression checks, file scope, and constitution rules against the current evidence. Check expected versus observed results and what cases actually ran; exit zero or AC references alone do not demonstrate acceptance. Do not substitute an opinion for failed, empty, unavailable, or stale evidence. Report a constitution MUST conflict as blocking. Verify the contributions and final checks assigned to this phase without demanding future-phase completion or treating partial task closure as final AC satisfaction.

Give a concise `pass` or `changes` verdict with concrete file/line or observable evidence, gaps/limitations, and the affected behavior/checks. Use existing phase-review fields; do not introduce acceptance states or another editable progress source. Do not alter the diff, approve human decisions, mark tasks complete, or integrate/publish the branch. Missing context or stale checks return to the orchestrator for authorized correction/refresh and a new stable review.

orchestrator reviews every task result; this separate session reviews the integrated phase, not every task independently. Changes to implementation/tree invalidate the review and require current affected evidence and a new review of the exact state to commit through valid controller transitions. An already reviewed/committed phase may block new preparation; return that state to the orchestrator for authorized reconciliation/restart rather than claiming refresh clears it. A passing review does not itself commit the phase, complete the release, or authorize external actions; those remain controller and downstream responsibilities.

Use [the profile contract](../contracts/profiles.md); current config edits never override a started run. No unavailable-model or effort fallback is permitted.
