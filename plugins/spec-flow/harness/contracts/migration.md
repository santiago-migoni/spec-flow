# Migrating legacy feature folders

This is a technical reference for moving a consuming project's legacy `.specs/NNN-name/` folders into release contracts. It does not decide product scope, release priorities, or approval on the user's behalf. The migration runtime only accepts an explicit mapping and a prepared candidate overlay; it does not infer those decisions from old prose.

Resolve `${CLAUDE_PLUGIN_ROOT}` from the installed Spec-Flow skill location. Every operation uses the portable entry point:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/spec-flow.py --root <absolute-project-root> migrate-preview --input <preview-input.json>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/spec-flow.py --root <absolute-project-root> migrate-apply --input <apply-input.json>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/spec-flow.py --root <absolute-project-root> migrate-resume --input <resume-input.json>
```

The CLI reads one JSON object from the input file, prints one JSON result, and exits 2 with an `error` object on a rejected operation. Ordinary harness operations reject legacy folders or an incomplete migration journal. Use `migrate-resume` for an interrupted apply.

## Prepare the source and candidates

The project must have a committed Git `HEAD` containing the exact original `.specs` files. The whole `.specs` tree must match that commit: no modified or untracked files, nonregular entries, or symlinks. The preview records the Git HEAD and SHA-256 of each source file. Commit the legacy source snapshot before preview; do not edit it between preview and apply.

Map every direct legacy directory exactly once. Each entry either selects one strict numeric SemVer release or archives a closed feature without an active release. Release identifiers are unique within a migration:

```json
{
  "mapping": [
    {"legacy": ".specs/001-demo", "release": "v2.0.0"},
    {"legacy": ".specs/002-retired", "archive": true}
  ],
  "candidate_dir": "/absolute/path/to/reviewed-candidates"
}
```

For any active release, `candidate_dir` is required. It is a directory containing only a `.specs/` overlay. Prepare the canonical documents explicitly from sourced decisions and human direction. Each active release needs complete `spec.md`, `plan.md`, and `tasks.md` in `.specs/release-vX.Y.Z/`. The overlay may also provide root strategy files (`constitution.md`, `architecture.md`, `structure.md`, `infrastructure.md`, `roadmap.md`) and `backlog.md`. It cannot contain an unmapped release or other nested paths. Preview validates the resulting release dependency graph and acceptance coverage in a temporary mirror. Missing required decisions, steps, file scopes, or expected verification must be resolved in the reviewed candidates; do not fill them with fabricated content. An archive-only mapping may use `candidate_dir: null`.

If an overlay replaces an existing root `.specs` file, add one `replacements` entry with its exact source byte hash and whole-document equivalence. The three `equivalence` strings are `statement`, `source_excerpt`, and `target_excerpt`; the excerpts must equal the complete old and candidate file contents. The replacement must be present in the overlay. A collision without this declaration is rejected. This records the conversion rationale; it does not import an old approval.

## Read-only preview

`migrate-preview` requires `mapping` and `candidate_dir`; optional fields are `replacements` (list) and `imports` (object with an optional `approvals` list). Preview reads the source and candidates, validates them, classifies approval import records, and returns:

- `manifest`: the exact project root, Git HEAD, source hashes, mapping, replacements, candidate path and hashes, import classifications, and deterministic migration ID.
- `digest`: SHA-256 of that canonical manifest.

It does not create `.spec-flow` or modify the project. Save the full result and review the candidate documents, mapping, replacements, and every import classification before apply. Changed source bytes, Git HEAD, candidate bytes, or import content invalidate the preview.

An optional import entry in the approvals list has exactly `source`, `target`, and `equivalence`. The source is a JSON file inside a mapped legacy directory; the target is the corresponding canonical document. Its equivalence object again contains `statement` and complete `source_excerpt`/`target_excerpt`. Import records may be `imported` or `pending` with a reason in the manifest. A pending record is archived as provenance and grants no approval.

## Apply and resume

`migrate-apply` input has exactly `manifest`, `digest`, `candidate_dir`, and `authorization`. Copy the complete manifest and digest from preview without editing them. `candidate_dir` must resolve to the same path. `authorization` has nonempty `actor`, `statement`, and `source` strings recording the human instruction to apply this specific conversion. This authorizes migration, not implementation or publication.

Before mutation, apply recomputes preview and rejects stale source, candidates, or import classifications. Under the project store lock it writes a journal at `.spec-flow/migrations/<migration_id>/journal.json`, stages candidate bytes, moves verified legacy folders to `.spec-flow/legacy/<migration_id>/sources/`, archives replaced root files there, promotes candidates, removes any remaining verified legacy source, validates the final releases, imports eligible records, initializes harness configuration, and writes `complete.json`. The original Git HEAD plus the verified archive preserve the exact old source. The result reports `completed`, `migration_id`, `source_git_head`, `archive`, active releases, and counts of imported and pending approvals.

If apply is interrupted, run `migrate-resume` with `{"migration_id":"<32 lowercase hex characters>"}`. Resume reads the journal and staged bytes, verifies hashes and any already promoted files, then continues. Repeating resume after completion is safe. If a destination or archive conflicts, it fails rather than overwriting unknown changes. A crash before the journal exists requires a fresh preview/apply. Keep the candidate directory available until the staging step has completed. The runtime deduplicates eligible approval imports by migration identity; repeated resume does not append them twice.

After successful migration, inspect and commit the converted canonical documents, provenance archive, and migration journal/completion marker before approving the converted release documents.

## Historical authority

An old `Status: Approved` table and checked task boxes are not registry approvals. Approval import requires a JSON record with exactly `schema_version: 1`, `kind: "spec-flow-approval-receipt"`, `path`, raw-file SHA-256 `digest`, `actor`, `statement`, and `source`. The original bytes must match the receipt. The target must match the mapped release or declared replacement, and its complete decision prose and structured decision fields must remain equivalent after excluding identity, revision, dependency, and status metadata. A changed acceptance decision stays pending and needs a new human approval of the converted document.

Feature-folder migration does not import execution history. Work in progress from a legacy folder is restarted under the new release.
