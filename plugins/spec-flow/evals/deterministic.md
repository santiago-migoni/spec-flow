# Deterministic evaluation — 2026-10-14

Source checkpoint: `d19cda7` (E6). Parent independently ran the full plugin suite: **97 tests passed** in 10.142 seconds. The documented hook suite passed **9 tests**. These tests exercise actual local validation, files, Git, commands, and failure recovery; native-model attestations in unit tests use explicitly labeled fixtures.

```bash
PYTHONPATH=plugins/spec-flow python3 -B -m unittest discover -s plugins/spec-flow/tests -p 'test_*.py'
python3 -B -m unittest discover -s plugins/spec-flow/hooks -p 'test_*.py'
```

| Scenario | Reproducible evidence in `tests/` | Result |
| --- | --- | --- |
| EV-01 Missing approval | `test_engine.test_start_requires_all_current_release_approvals` | Blocks before execution |
| EV-03 Legacy data | `test_migration.test_apply_archives_sources_promotes_candidate_and_does_not_import_checkmarks` | Originals preserved; labels/boxes confer no authority |
| EV-04 Stale code | `test_engine.test_changes_after_verification_are_rechecked_before_review`; `test_phases` post-audit changes | Blocks stale or unreviewed code, including committed changes |
| EV-05 Interruption | `test_engine` resume/reconciliation, late bind and no-spawn tests; `test_phases` crash adoption | Reconciles existing attempt; does not blindly replay |
| EV-06 Duplicate close | `test_engine.test_close_requires_review_records_checkbox_and_is_idempotent` | One completion effect |
| EV-07 Retry bound | `test_engine.test_task_attempts_stop_after_three_rejected_reviews`; abandon/restart carryover | Three attempts total; restart cannot reset budget |
| EV-08 Scope | `test_engine.test_out_of_scope_changes_fail_verification`, retry baseline regression | Out-of-scope writes cannot be accepted or laundered by retry |
| EV-09 Empty tests | `test_engine.test_verify_rejects_empty_and_zero_test_results` | Empty/zero-case output fails |
| EV-10 Identity | `test_codex_adapter` capability, profile, lineage and prompt-marker tests | Missing/mismatched evidence fails closed |
| EV-12 Closure | `test_phases` technical completion, derived review, final audit lease and crash tests | Technical, impact and publication states remain separate |
| EV-13 Two owners | `test_codex_adapter.test_linked_worktree_shares_persistent_repository_lease` | Shared common-directory lease rejects competing ownership |
| EV-14 Corrupt journal | `test_engine.test_corrupt_event_log_fails_closed_and_state_rebuilds_from_events` | Corruption blocks; valid events rebuild missing state |
| EV-15 Changed decisions | `test_engine.test_approval_change_invalidates_run_before_close` | Exact changed source invalidates approval correspondence |

EV-02 requires the separately recorded native Codex evaluation. EV-11 decision routing is covered by `skill-behavior.md`; semantic consistency of arbitrary prose remains a model review responsibility, not a claim of deterministic semantic proof.

Additional coverage includes migration collisions, interrupted promotion, exact historical evidence reuse, changed acceptance refusing imported approval, strict derived fields, dependency/cycle/acceptance validation, isolated production worktrees, and scope checks for supported hook aliases. Hook tests do not establish that a real user has trusted the installed hook.

## Post-native corrections and final E7 checkpoint

After native evaluation exposed host-log incompatibility and stale retry binding, the full package suite passed **107 tests**, and the documented hook suite passed **9**. Additional regressions cover encrypted native invocation binding with exact call-linked output, retry binding/time reset, and explicit task/phase packet restoration. `restore-packet` preserves the hash, attempt and bound agent, refuses stale sources/corrupt caches, and diagnoses old missing timestamps. A separate Sol review found no blocker in these changes. Restoration coverage here is deterministic; the native report records the previously completed production flows and their exact runtime hashes.
