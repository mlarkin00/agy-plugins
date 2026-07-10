#!/usr/bin/env bash
# Health check for the Jetski agent memory system.
# Tier 2 checks detect structural failures and prompt the user to run bootstrap-memory.
# Tier 1 checks auto-fix minor drift (broken symlink, missing GEMINI.md) silently.
# Outputs nothing on a healthy system.

REPO="$HOME/.agents/agent-memory"
SYMLINK="$HOME/.gemini/GEMINI.md"
TIER2=0

# ── Tier 2 checks — structural failures; prompt bootstrap ─────────────────────

if [[ ! -d "$REPO" ]]; then
  echo "[verify-memory] ⚠ Repo not found at $REPO. Run the bootstrap-memory agent to set up." >&2
  TIER2=1
fi

if [[ "$TIER2" -eq 0 && ! -d "$REPO/.git" ]]; then
  echo "[verify-memory] ⚠ $REPO is not a git repo. Run the bootstrap-memory agent to restore." >&2
  TIER2=1
fi

if [[ "$TIER2" -eq 0 ]]; then
  REMOTE=$(git -C "$REPO" remote get-url origin 2>/dev/null || echo "")
  if [[ "$REMOTE" != *"agent-memory"* ]]; then
    echo "[verify-memory] ⚠ Remote '$REMOTE' does not match expected repo. Run the bootstrap-memory agent to restore." >&2
    TIER2=1
  fi
fi

# Stop here if any Tier 2 failure — no point fixing minor issues on a broken foundation
if [[ "$TIER2" -eq 1 ]]; then
  exit 1
fi

# ── Tier 1 checks — auto-fix silently ────────────────────────────────────────

# Hooks symlink missing or broken
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLUGIN_ROOT="$( dirname "$SCRIPT_DIR" )"
HOOKS_SYMLINK="$HOME/.gemini/jetski/hooks.json"
HOOKS_TARGET="$PLUGIN_ROOT/hooks.json"

if [[ -e "$HOOKS_SYMLINK" && ! -L "$HOOKS_SYMLINK" ]]; then
  echo "[verify-memory] ⚠ $HOOKS_SYMLINK exists and is not a symlink. Skipping." >&2
else
  mkdir -p "$HOME/.gemini/jetski"
  ln -sfn "$HOOKS_TARGET" "$HOOKS_SYMLINK"
fi

# Symlink missing or broken
if [[ -e "$SYMLINK" && ! -L "$SYMLINK" ]]; then
  echo "[verify-memory] ⚠ $SYMLINK exists and is not a symlink. Skipping." >&2
else
  ln -sfn "$REPO/GEMINI.md" "$SYMLINK"
fi

# GEMINI.md missing
if [[ ! -f "$REPO/GEMINI.md" ]]; then
  printf "# Global Memories\n\n" > "$REPO/GEMINI.md"
  git -C "$REPO" add GEMINI.md
  git -C "$REPO" commit -m "memory: create GEMINI.md" 2>/dev/null || true
fi

exit 0
