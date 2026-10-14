# Baseline before harness skills

Date: 2026-10-14. Source: original skills at 935de5d. Read-only native Codex agent `/root/skills_baseline`, explicitly selected gpt-6-sol, medium effort.

Scenario: legacy `.specs/001-demo` documents are Approved; tasks are checked without test evidence; user requests release v2.0.0, Luna implementation and all phases under deadline pressure.

Observed response: current implement accepts artifact statuses, runs check-complete for checked tasks, reports ready for converge without an empty commit. The script only searches unchecked boxes. Converge inspects code after an implement pass; it cannot establish historical execution evidence. For unfinished work the skill requires one phase, then stops. No migration, release-oriented document workflow, ledger or Luna routing commands exist.

Required new behavior: detect legacy artifacts and require explicit one-to-one migration; preserve history without treating checkboxes as evidence; use a capability-attested Luna task packet, approval and execution scope; stop when that authorized scope ends. These are functional gaps in the old skills, not measured model error rates.

This single baseline is not a statistical behavioral benchmark. Post-change scenarios must separately exercise actual runtime operations and native delegation; static instruction checks alone do not prove end-to-end activation.

## Measured single-model reference — 2026-10-14

A fresh `gpt-6-sol` / `high` session implemented a strict Python `normalize_release` function in `/private/tmp/spec-flow-e7-reference-k5fExg` without the harness or subagents. It accepts exact `X.Y.Z` or `vX.Y.Z` strings, rejects leading zeros, whitespace, suffixes and malformed components with `ValueError`, and rejects nonstrings with `TypeError`.

- Host session: `01a13b3b-312e-71b2-bdcd-ee7ba52cf7a0`; parent `01a13adc-9094-7710-a4f5-d9a365a176b5`.
- Host `turn_context`: `gpt-6-sol`, reasoning effort `high`.
- Host task duration: **54,371 ms**. Agent-observed work timestamps: 16:25:06–16:25:44 UTC; these measure a narrower interval and are not interchangeable with host duration.
- Verification: `python3 -B -m unittest -v test_release.py`, 4 test methods passed after the expected missing-module failure before implementation.
- `release.py` SHA256: `a3cc0ce61d2ee3481ae9587ae96a0e8fb41bc7a9c267fa93cc1f622ac97e098a`.
- `test_release.py` SHA256: `7bb24f05e31ffe3fdb53c96895e3462a5823fe7ac9ad4bdbe0e612d206cd0577`.
- Final host `token_count.info.total_token_usage`: input 212,844; cached input 168,192; cache-write input 0; output 2,458; reasoning output 932; total 215,302. These are cumulative session counters including repeated system/tool context, not a standalone task price.
- Reported correction rounds: 0; reported blockers: 0. The initial red test is test-first setup, not a failed implementation correction.

This is one small reference task. The native harness evaluation must use equivalent acceptance and checks and report orchestration/setup separately where observable. No cost, speed, or quality advantage is established by this reference alone; token counters are reported as exposed by this host; monetary cost has not been measured.

The reference source and independently rerun test output are retained under `reference/` in this evaluation directory.
