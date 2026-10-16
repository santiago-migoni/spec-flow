# Configurable native role profiles

`.spec-flow/config.json` holds `schema_version: 1`, exactly three model/effort profiles, and `retry_limit: 3`. This is controller configuration, not native Codex agent definitions. It does not launch models, approve sources or authorize execution. Manifests and the installation's version are unrelated to project profile selection.

Newly initialized projects use:

```json
{
  "schema_version": 1,
  "profiles": {
    "orchestrator": {"id": "gpt-6.1-sol", "effort": "low"},
    "implementer": {"id": "gpt-6-luna", "effort": "high"},
    "reviewer": {"id": "gpt-6.1-sol", "effort": "medium"}
  },
  "retry_limit": 3
}
```

Existing valid project configs are preserved by initialize and legacy-folder migration. Change only the requested profiles using `configure-profiles` with `{"profiles":{...}}` containing all three roles, each with exactly `id` and `effort`. The operation validates and atomically writes configuration, is idempotent, and grants no execution permission. Humans can edit the JSON directly; agent-controlled updates use this operation rather than patching protected registry paths. Invalid JSON/config must be corrected before controller mutations. Never change the retry budget to bypass failed attempts.

Model IDs are nonempty host identifiers without whitespace (letters, digits, dot, underscore, colon, slash and hyphen, at most 128 characters). Recognized effort labels are none, minimal, low, medium, high, xhigh, max and ultra; actual host/model support is checked separately. There is no model-family allowlist and no silent substitute. A valid identifier does not prove availability or effectiveness.

## Availability and actual identity

Before a new run, inspect the current host's model inventory, confirm all three configured model/effort pairs, and retain an evidence reference. Native `capabilities`/`start` reports require these additional fields:

```json
{
  "model_catalog_reference": "reference to the current native host model inventory",
  "model_catalog": [
    {"id": "gpt-6.1-sol", "reasoning_efforts": ["low", "medium"]},
    {"id": "gpt-6-luna", "reasoning_efforts": ["high"]}
  ]
}
```

Merge these with the existing operations, probe_evidence and inventory_reference fields. Do not fabricate catalog entries or reference evidence from another host. The controller checks the host-supplied snapshot and persists it with the capability record; Python cannot independently enumerate or authenticate external inventory references. Missing models, unsupported efforts, missing/invalid catalogs or failed spawn calls block execution rather than selecting another model.

Availability evidence never replaces attestation: the orchestrator, implementer and independent reviewer must each match the configured exact model/effort in all relevant native session turns. Encrypted delegation additionally binds the actual spawn model/effort, task name, parent/path and returned native identity to the prepared marker. The reviewer remains a separate completed session from the owner and all implementers even if models are the same. One implementer and three attempts remain mandatory.

## Run snapshots and compatibility

`started` persists a validated `profiles` copy. Rebuilt state and all later native checks use that immutable choice, including repeated start, prepare, resume/reconcile, takeover, task/phase review, audit and release of ownership. Current configuration edits affect only newly created runs; they do not change existing authorization, model identity, packets, retry counts or events. Inspect stored run profiles before selecting/spawning an owner for resumption. `capabilities` accepts an optional `run_id` to attest the matching existing owner against that run instead of current configuration.

New task and phase packets include the snapshot in their hashed payload; packet recovery reproduces the same bytes. Old start events without profiles are interpreted with the historical fixed Sol/high–Luna/high–Sol/high profiles (`gpt-6-sol`, `gpt-6-luna`, `gpt-6-sol`). Their original events/evidence and packet format/hashes are not rewritten. This compatibility rule is not a fallback for invalid snapshots: malformed recorded profiles fail closed.

Historical E7/E8 results retain their evaluated model choices. Configurability or deterministic tests do not prove a new combination is effective, available on another host, or natively evaluated. A new native evaluation records its actual selected profiles and scope.
