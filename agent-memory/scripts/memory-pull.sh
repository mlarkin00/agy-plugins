#!/usr/bin/env bash
# Pulls the latest memory state from GitHub. Remote always wins.
# Called by the SessionStart hook in agent-memory-extension/hooks/hooks.json.

set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  echo "Usage: $0"
  echo "Pulls the latest memory state from GitHub."
  echo ""
  echo "Example:"
  echo "  $0"
  exit 0
fi

# Run verify to ensure health (including hooks symlink)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
bash "$SCRIPT_DIR/verify-memory-jetski.sh"

TIMESTAMP_FILE="$HOME/.gemini/jetski/.memory-pull-timestamp"
mkdir -p "$(dirname "$TIMESTAMP_FILE")"
CURRENT_TIME=$(date +%s)

if [[ -f "$TIMESTAMP_FILE" ]]; then
  LAST_PULL=$(cat "$TIMESTAMP_FILE")
  if (( CURRENT_TIME - LAST_PULL < 300 )); then
    echo "[memory-pull] SKIP: pulled recently" >&2
    exit 0
  fi
fi

REPO="$HOME/.agents/agent-memory"

if [[ ! -d "$REPO/.git" ]]; then
  echo "[memory-pull] SKIP: repo not found at $REPO" >&2
  exit 0
fi

cd "$REPO"
git fetch origin >/dev/null || { echo "[memory-pull] WARNING: fetch failed" >&2; exit 0; }
git reset --hard origin/main >/dev/null || { echo "[memory-pull] ERROR: reset failed" >&2; exit 1; }

echo "$CURRENT_TIME" > "$TIMESTAMP_FILE"
