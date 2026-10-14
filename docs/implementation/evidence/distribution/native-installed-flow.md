# E8 native installed-plugin flow

- Host: Codex Desktop/0.135.0 on macOS arm64, reported by the local Codex app-server `initialize` response.
- Discovery: a fresh `codex app-server --listen stdio://` client called `skills/list` with `cwds=["/private/tmp/spec-flow-e8-evaluation/clean-session-project"]` and `forceReload=true`. The response had no errors and returned 16 enabled `spec-flow-e8-01a13adc:*` user skills. The complete filtered result is in `discovered-skills.json`.
- Installed bootstrap skill: `spec-flow-e8-01a13adc:using-spec-flow` at `/Users/santiago_migoni/.codex/plugins/cache/spec-flow-e8-market-01a13adc/spec-flow-e8-01a13adc/1.1.0/skills/using-spec-flow/SKILL.md`. Its installed plugin root was resolved as `/Users/santiago_migoni/.codex/plugins/cache/spec-flow-e8-market-01a13adc/spec-flow-e8-01a13adc/1.1.0`.
- The scratch project contained only `.git` before initialization. The installed bootstrap instructed `initialize` with `{}`, then `status` and the intended phase gate.
- Installed runtime command: `python3 /Users/santiago_migoni/.codex/plugins/cache/spec-flow-e8-market-01a13adc/spec-flow-e8-01a13adc/1.1.0/scripts/spec-flow.py --root /private/tmp/spec-flow-e8-evaluation/clean-session-project OP --input JSON_FILE`.
- `initialize --input empty-input.json`: exit 0, `{"already_initialized": false, "config_path": "/private/tmp/spec-flow-e8-evaluation/clean-session-project/.spec-flow/config.json", "status": "initialized"}`.
- `status --input empty-input.json`: exit 0, `{"initialized": true, "runs": [], "status": "initialized"}`.
- `gate --input constitution-gate.json` with `{"kind":"constitution"}`: exit 0, `{"invalid_prerequisites": [], "missing_approvals": [], "ready": true}`.
- Next decision: a constitution draft is permitted by the gate, but this test stops before drafting, approval, implementation, installation changes, or trust changes. The initial app-provided skill catalog was not tested for automatic refresh; this confirms a fresh app-server discovery request and use of the installed runtime.
