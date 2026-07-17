#!/bin/bash
# ponytail: fail-open ONLY for an existing artifact with no Status column (grandfathered,
# pre-this-feature format). No resolvable branch/artifact at all denies instead — see
# .specs/003-phase-approval-gate/spec.md's Clarifications for why the two cases differ.
set -eu

allow() { echo '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}'; exit 0; }
deny() { printf '{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny"}, "systemMessage": "%s"}\n' "$1"; exit 0; }

input=$(cat)

tool_name=$(printf '%s' "$input" | sed -n 's/.*"tool_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
[ "$tool_name" = "Skill" ] || allow

skill=$(printf '%s' "$input" | sed -n 's/.*"skill"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')

case "$skill" in
  spec-flow:specify)
    artifact=".specs/constitution.md"
    ;;
  spec-flow:plan|spec-flow:tasks|spec-flow:implement)
    branch=$(git branch --show-current 2>/dev/null) || deny "Can't determine the current feature (no git branch) — make sure you're on a feature branch before running ${skill}."
    [ -n "$branch" ] || deny "Can't determine the current feature (no git branch) — make sure you're on a feature branch before running ${skill}."
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

[ -f "$artifact" ] || deny "${artifact} doesn't exist — make sure you're on the correct feature branch and that the prior phase has completed."

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
  deny "${artifact} has Status: Draft — ask the user to approve it before running ${skill}."
else
  allow
fi
