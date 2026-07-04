#!/bin/bash
# Returns the next zero-padded 3-digit feature number based on existing .specs/ directories.
# Usage: ./scripts/next-feature-number.sh [specs-dir]
# Output: e.g., "003"

SPECS_DIR="${1:-.specs}"

LAST=$(ls -d "${SPECS_DIR}"/[0-9][0-9][0-9]-* 2>/dev/null \
  | xargs -I{} basename {} \
  | grep -oE '^[0-9]{3}' \
  | sort -n \
  | tail -1)

if [ -z "$LAST" ]; then
  printf '%03d\n' 1
else
  printf '%03d\n' $((10#$LAST + 1))
fi
