---
name: uninstall-memory-jetski
description: Use when the user wants to uninstall or clean up the agent-memory extension for Jetski. Handles removal of symlinks and hooks.
---

You are uninstalling the agent-memory extension for Jetski. Work through each step in order.

## Step 1: Remove script and agent symlinks

```bash
rm -f \
  ~/.gemini/scripts/memory-pull.sh \
  ~/.gemini/scripts/memory-push.sh \
  ~/.gemini/scripts/verify-memory-jetski.sh \
  ~/.gemini/scripts/memory_push_trigger.py \
  ~/.gemini/agents/memory-puller-jetski \
  ~/.gemini/agents/memory-pusher-jetski
echo "✓ Script and Agent symlinks removed"
```

## Step 2: Remove the GEMINI.md symlink

```bash
if [[ -L "$HOME/.gemini/GEMINI.md" ]]; then
  rm "$HOME/.gemini/GEMINI.md"
  echo "✓ GEMINI.md symlink removed"
fi
```

## Step 3: Uninstall the extension

```bash
jetski extensions uninstall agent-memory
```

## Step 4: Final summary

> "The agent-memory extension has been uninstalled. Your memory repo at `~/.agents/agent-memory` is preserved."

```
