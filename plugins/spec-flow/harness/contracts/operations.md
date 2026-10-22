# Shared controller operations

The controller records approvals of documents and checks their dependencies. It does not run, delegate, review, or track implementation. Each skill keeps its own HARD-GATE, mode restrictions, and semantic checks.

## Controller invocation

Resolve `${CLAUDE_PLUGIN_ROOT}` from the installed SKILL.md and use the consuming `<project>` root. Invoke:

```sh
python3 -B ${CLAUDE_PLUGIN_ROOT}/scripts/spec-flow.py --root <project> OP --input <json-file>
```

Inputs are JSON objects, results are JSON on stdout, and rejected operations return an error object with exit code 2. Supported operations are `initialize`, `digest`, `validate`, `approve`, `gate`, `hook-check`, `migrate-preview`, `migrate-apply`, and `migrate-resume`. Do not invent other commands.

## Read-only queries

For a consultation or read-only review, create no files: no report, input file, approval, or migration preview written to disk. The read-only operations are:

| Operation | Input |
| --- | --- |
| `digest` | `{"path":"<supported document>"}` |
| `validate` | `{"path":"<supported document>"}` or `{"release":"vX.Y.Z"}` once spec, plan, and tasks exist |
| `gate` | `{"path":"<supported document>"}`, `{"phase":"<phase>","release":"vX.Y.Z"}`, or `{"kind":"<kind>","release":"vX.Y.Z"}` |

Use `/dev/stdin` for inline input on POSIX hosts, and disable Python bytecode writes with `-B`.

## Adoption

For a new unadopted project, run `initialize` with `{}` before the first document approval. This writes `.spec-flow/config.json` and a lock file, and nothing else. Legacy `.specs/NNN-name/` directories require the [migration contract](migration.md): `migrate-preview` → human review → `migrate-apply`. An interrupted apply uses `migrate-resume`.

## Documents and gates

The [canonical contract](canonical-contract.md) defines the supported document kinds. Each document carries stable identity, a revision starting at R00, exact-digest `depends_on`, and decision prose.

Before writing a dependent document, run its gate and check that every source it uses is approved. A failed gate blocks the dependent work. The approval order is:

constitution → architecture / infrastructure / structure (as applicable) → roadmap → release `spec` → release `plan` → release `tasks`.

A roadmap change requires its own approval before any release document that depends on it can be approved again. Backlog items and conversational reports have no controller contract and are never approved.

## Approval and revisions

Present the validated draft before asking for approval. On explicit approval, call `approve` with `{"path":"<project-relative document>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. Do not approve unseen changes on the user's behalf.

Approval state lives in the header `status` (`draft` or `approved`) and in the registry, never in the prose. `approve` sets `status: approved`, validates the result, and records the digest. The status is outside the digest, so the digest of a draft is the one that stays recorded and any pin taken from it stays valid. A document without a YAML header is approved as before, and a document already marked `approved` is left alone, so retries keep the same receipt. Report approval state from `gate` or the receipt. `validate` warns when the status is `approved` but no current receipt exists, for example after a later edit. Start each new revision with `status: draft`.

## Document encoding

New canonical documents use YAML frontmatter before the title. Existing fenced `spec-flow` JSON documents keep their encoding unless the user explicitly authorizes conversion. Conversion changes the digest and requires re-approval. CLI payloads and internal records remain JSON.
