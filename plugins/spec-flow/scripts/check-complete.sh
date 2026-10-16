#!/bin/sh
# Evidence and phase-commit completion check for a release tasks.md.
# Preserves decisions/evidence; uses a temporary input and Git may refresh its index.
# Not a strict no-file consultation query; see harness/contracts/operations.md.
# Exit 0 means complete, 1 means valid but incomplete, 2 means invalid input/runtime error.

if [ "$#" -ne 1 ] || [ -z "$1" ] || [ ! -f "$1" ]; then
  echo "Usage: $0 <path-to-.specs/release-vX.Y.Z/tasks.md>" >&2
  exit 2
fi

tasks_dir=$(CDPATH= cd "$(dirname "$1")" 2>/dev/null && pwd -P) || exit 2
tasks_name=$(basename "$1")
release_dir=$(basename "$tasks_dir")
specs_dir=$(dirname "$tasks_dir")
if [ "$tasks_name" != "tasks.md" ] || [ "$(basename "$specs_dir")" != ".specs" ]; then
  echo "Expected a canonical .specs/release-vX.Y.Z/tasks.md path." >&2
  exit 2
fi
case "$release_dir" in
  release-v*) release=${release_dir#release-} ;;
  *) echo "Invalid release directory: $release_dir" >&2; exit 2 ;;
esac
case "$release" in
  *[!0-9.v]*|v|.*|*.) echo "Invalid release identifier: $release" >&2; exit 2 ;;
esac
if ! printf '%s' "$release" | grep -Eq '^v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$'; then
  echo "Invalid release identifier: $release" >&2
  exit 2
fi

project_root=$(dirname "$specs_dir")
script_dir=$(CDPATH= cd "$(dirname "$0")" 2>/dev/null && pwd -P) || exit 2
plugin_root=$(dirname "$script_dir")
input_file=$(mktemp "${TMPDIR:-/tmp}/spec-flow-complete.XXXXXX") || exit 2
trap 'rm -f "$input_file"' EXIT HUP INT TERM
printf '{"release":"%s"}\n' "$release" >"$input_file" || exit 2

result=$(python3 "$plugin_root/scripts/spec-flow.py" --root "$project_root" complete --input "$input_file")
status=$?
if [ "$status" -ne 0 ]; then
  printf '%s\n' "$result" >&2
  exit 2
fi
complete=$(printf '%s' "$result" | python3 -c 'import json,sys; value=json.load(sys.stdin); print("true" if value.get("complete") is True else "false")' 2>/dev/null) || exit 2
if [ "$complete" = "true" ]; then
  exit 0
fi
printf '%s\n' "$result" >&2
exit 1
