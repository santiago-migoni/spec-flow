# Shared controller operations

Read the sections relevant to the owning skill's requested mode before controller use. These mechanics do not replace its HARD-GATE, prerequisite approvals, semantic review, authorization scope, or execution/recovery protocol. No operation here authorizes a later phase or an external action.

## Controller invocation

Resolve `<plugin-root>` from the installed SKILL.md and establish the consuming `<project>` root. Invoke `python3 -B <plugin-root>/scripts/spec-flow.py --root <project> OP --input <json-file>`. `-B` prevents import caches in the plugin; it does not make a mutating operation read-only. Inputs are JSON objects, results are JSON on stdout, and rejected operations return an error object with exit code 2. Use actual supported operations and fields rather than inventing a `migrate` command or a gate kind.

## Strict consultation

For consultation or a read-only review, create no files: no report, input/scratch file, Python cache, setup, migration (including preview), repair, approval, progress update, evidence refresh, or execution. Inspect task/check definitions without running them. The query whitelist is:

| Operation | Input and boundary |
| --- | --- |
| `status` | `{}` for adoption/run summaries. Inspect existing durable records for historical detail; history does not establish current technical completion. |
| `validate` | `{"path":"<supported document>"}` or `{"release":"vX.Y.Z"}` only when the owning skill requires full-release validation and all three release documents exist. |
| `digest` | `{"path":"<supported document>"}` for decision-content digests. |
| `gate` | `{"kind":"<supported phase>","release":"vX.Y.Z"}` for the intended release phase; omit release for a strategic kind. A path-based gate checks document prerequisites and does not replace a required phase gate. |

Use existing input files or stream JSON through `/dev/stdin` on the supported POSIX host. Disable optional locking for child Git reads and bytecode writes for Python:

```sh
printf '%s' '{}' |
  GIT_OPTIONAL_LOCKS=0 python3 -B "<plugin-root>/scripts/spec-flow.py" --root "<project>" status --input /dev/stdin
```

For direct Git reads use `git --no-optional-locks`, without refreshing the index. Exclude `complete` and `check-complete.sh` from this mode as explained below. Do not invoke `capabilities`, task checks, or recovery as queries. On missing adoption, legacy artifacts, failed validation, or another query error, preserve the diagnostic and route the prerequisite to its authorized owner; consultation itself performs no repair. If no safe input channel is available, report that limitation.

## Adoption before authorized writes

Inspect project configuration and `.specs` before writing. For a new nonlegacy unadopted project, run `initialize` with `{}` before the first authorized write. This is adoption, not migration. Legacy `.specs/NNN-name/` directories require the [migration contract](migration.md): exact committed originals, explicit mapping and reviewed candidates, `migrate-preview` → human review → `migrate-apply`. An interrupted apply uses `migrate-resume`. Historical Approved text or checked boxes cannot supply current authority/evidence. Adoption does not waive the owning skill's gate.

## Governed documents and gates

The [canonical contract](canonical-contract.md) defines the eight supported source kinds and their fields. New documents use one YAML frontmatter header before the title; existing fenced `spec-flow` JSON documents retain their encoding unless conversion is explicitly authorized. Both retain stable kind/id, revision R00 initially, exact-digest `depends_on`, and decision prose. Registry approval of exact content and its dependency closure is authority; generated progress and optional top-level lowercase `status` are views.

Before writing dependent decisions, run the owning phase gate and inspect current approvals of all sources actually used. A failed gate blocks dependent work; a narrower query cannot bypass it. `design` uses the actual `architecture`, `infrastructure`, or `structure` kind. `using-spec-flow`, `design`, and `backlog` are not gate kinds. Backlog and conversational reports have no controller document contract: do not validate, digest, or approve them.

Validate the supported document path after drafting; obtain its digest with the same path input when needed for dependencies. Spec and plan preparation validate their own path without requiring future documents. Tasks, analyze, and implementation retain their required full-release validation with `{"release":"vX.Y.Z"}` once spec/plan/tasks exist. Progressive elaboration does not waive full-release tasks or AC coverage. Structural validation does not prove semantic sufficiency or Markdown table coherence; each owner retains those checks.

## Approval and revisions

Present the concrete validated draft before human approval or dependent work. On explicit approval, the owning skill calls `approve` with `{"path":"<project-relative document>","actor":"<human>","statement":"<their approval>","source":"<conversation reference>"}`. Reuse an existing declaration when its exact proposed wording and scope cover all resulting content; do not ask again redundantly or approve unseen changes on the user's behalf. Read-only skills never record approval; route accepted corrections to the writing owner.

Keep R00 until first approval. A substantive postapproval edit increments RNN once; further review rounds and interrupted amendment drafts retain that revision until approved. Old receipts do not approve changed content. Inspect affected downstream pins and adopt a new base only with explicit approval. Preserve stable identities, unchanged approved sources, and historical evidence. Reconcile active execution before changing governing bases using the [execution contract](execution.md); document approval does not authorize implementation, integration, publication, or deployment.

## Completion checks

`complete` accepts `{"release":"vX.Y.Z"}` and optional `run_id`. It evaluates current source pins, task evidence, reviewed phase commits, and pending review/audit conditions. It does not alter source decisions, approval receipts, or execution evidence, but its Git comparisons can refresh the index even with optional locking disabled. `bash <plugin-root>/scripts/check-complete.sh <canonical tasks.md>` also creates a temporary input and may generate Python caches. Neither is a strict no-file query. Do not change Git configuration to force a consultation result.

In strict consultation, inspect existing status/events/closure references as recorded history and explicitly state that current technical completion, review/audit flags, and closure eligibility were not revalidated. Do not infer readiness from those records.

Authorized implementation handoff, convergence, release review, finishing, and recovery retain their required live completion checks under their existing gates and scope. This filesystem limitation never waives them. `complete.technical_complete=true` is technical eligibility, not semantic convergence, closure approval, or execution/integration authority. `release_review_pending` and `audit_pending` describe remaining closure; require their applicable values at the owning stage. Missing values do not pass. The wrapper maps technical completion to exit 0, incomplete to 1, and invalid input/runtime errors to 2. Concrete execution payloads and closure/recovery controls remain in the [execution contract](execution.md).

## Document encoding and explicit conversion

Create new canonical documents with YAML frontmatter before the title, following [the canonical contract](canonical-contract.md). Metadata and kind-specific records remain one canonical source; do not retain a second fenced JSON contract. CLI payloads/results and internal records remain JSON.

Existing JSON decision documents are supported without automatic conversion, including mixed-format dependency chains. Preserve their encoding during scoped edits and generated status updates unless the user authorizes conversion. Conversion of approved content changes its digest and requires the applicable revision/approval and explicit downstream adoption; old receipts and evidence remain historical. Reconcile active execution before changing its sources. Consultation and resumption never perform conversion, rewrite pins or restore approval.

## Role model preferences

For an explicitly requested model/effort change, follow [configurable profiles](profiles.md) and use `configure-profiles` with all three profiles. This is a mutating configuration operation, excluded from strict consultation. It does not authorize execution or change existing runs. Preserve retry_limit=3, current approvals and evidence. New-run capability probes include host model/effort inventory evidence; resumed runs use their frozen profiles.
