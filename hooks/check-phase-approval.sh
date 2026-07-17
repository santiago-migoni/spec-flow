#!/bin/bash
# ponytail: fail-open by design — this hook reinforces the prose <HARD-GATE>, it is not the sole line of defense.
set -eu

allow() { echo '{"hookSpecificOutput": {"permissionDecision": "allow"}}'; exit 0; }

input=$(cat)

tool_name=$(printf '%s' "$input" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ "$tool_name" = "Skill" ] || allow

skill=$(printf '%s' "$input" | sed -n 's/.*"skill"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')

case "$skill" in
  spec-flow:specify)
    artifact=".specs/constitution.md"
    ;;
  spec-flow:plan|spec-flow:tasks|spec-flow:implement)
    branch=$(git branch --show-current 2>/dev/null) || allow
    [ -n "$branch" ] || allow
    case "$skill" in
      spec-flow:plan) artifact=".specs/${branch}/spec.md" ;;
      spec-flow:tasks) artifact=".specs/${branch}/plan.md" ;;
      spec-flow:implement) artifact=".specs/${branch}/tasks.md" ;;
    esac
    ;;
  *)
    allow
    ;;
esac

[ -f "$artifact" ] || allow

status=$(awk -F'|' '
  /^\|/ { n++ }
  n == 3 {
    field = $(NF-1)
    gsub(/^[ \t]+|[ \t]+$/, "", field)
    print field
    exit
  }
' "$artifact")

if [ "$status" = "Draft" ]; then
  printf '{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "%s has Status: Draft \xe2\x80\x94 ask the user to approve it before running %s."}\n' "$artifact" "$skill"
else
  allow
fi
