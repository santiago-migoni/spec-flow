#!/bin/bash
# Checks whether all tasks in a tasks.md are marked [x].
# Usage: ./scripts/check-tasks-complete.sh <path-to-tasks.md>
# Exit 0: all done. Exit 1: unchecked tasks remain. Exit 2: bad usage.

TASKS_FILE="$1"

if [ -z "$TASKS_FILE" ]; then
  echo "Usage: $0 <path-to-tasks.md>" >&2
  exit 2
fi

if [ ! -f "$TASKS_FILE" ]; then
  echo "File not found: $TASKS_FILE" >&2
  exit 2
fi

UNCHECKED=$(grep -c '^- \[ \]' "$TASKS_FILE" 2>/dev/null)

if [ "$UNCHECKED" -eq 0 ]; then
  echo "All tasks complete."
  exit 0
else
  echo "${UNCHECKED} task(s) not yet complete." >&2
  grep '^- \[ \]' "$TASKS_FILE" >&2
  exit 1
fi
