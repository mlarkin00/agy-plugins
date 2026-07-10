# Design: Redesign Agent Memory Plugin for Jetski

**Date**: 2026-05-20
**Status**: Approved

## Goal
Redesign the `agent-memory-jetski` plugin to work correctly within the Jetski environment, replacing the legacy `jetski-agent-memory` plugin. This involves porting from Gemini CLI hooks to Jetski hooks and making the plugin self-contained.

## Architecture & Components

The plugin manages agent memory across sessions using a global `GEMINI.md` file backed by a Git repository.

### Components:
*   **Agents** (in `agents/`):
    *   `bootstrap-memory-jetski`: Provisions the memory system.
    *   `memory-puller-jetski`: Manual trigger to pull latest memory.
    *   `memory-pusher-jetski`: Manual trigger to push memory changes.
*   **Scripts** (in `scripts/`):
    *   `memory-pull.sh`: Fetches and resets local memory to remote state.
    *   `memory-push.sh`: Commits and pushes local memory changes.
    *   `memory_push_trigger.py`: Decides if a push is needed after a tool call.
    *   `verify-memory-jetski.sh`: Health check script.
*   **Skills** (in `skills/`):
    *   `add-memory`: Skill for agents to add memories.
    *   `uninstall-memory`: Cleanup skill.
    *   `verify-memory`: Verification skill.

## Redesign Details

### 1. Hooks Configuration (`hooks.json`)
We will create a `hooks.json` file at the plugin root to replace the Gemini CLI hook mechanism.

```json
{
  "agent-memory-pull": {
    "PreInvocation": [
      {
        "type": "command",
        "command": "./scripts/memory-pull.sh"
      }
    ]
  },
  "agent-memory-push": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "python3 ./scripts/memory_push_trigger.py"
      }
    ]
  }
}
```

### 2. Self-Containment & Path Updates
*   Remove `scripts/install-symlinks-jetski.sh`.
*   Update agent `config.yaml` files to use relative paths (e.g., `./scripts/memory-pull.sh`) instead of hardcoded `~/.gemini/scripts/` paths.
*   Rely on Jetski's automatic discovery of agents in the plugin's `agents/` directory.

### 3. Script Modifications
*   **`memory-pull.sh`**: Add a 5-minute throttle check using a timestamp file to avoid overhead during `PreInvocation`.
*   **`memory_push_trigger.py`**: Rewrite to read the `transcript.jsonl` file provided by Jetski's `PostToolUse` hook on `stdin` (specifically `transcriptPath` and `stepIdx`) to determine if `GEMINI.md` was modified.

## Data Flow
1.  **Session Start**: `PreInvocation` hook triggers `memory-pull.sh` (if not throttled), fetching latest memories.
2.  **Agent Interaction**: Agent uses `add-memory` skill to edit `GEMINI.md`.
3.  **Post Tool Use**: `PostToolUse` hook triggers `memory_push_trigger.py` after write tools.
4.  **Trigger Decision**: `memory_push_trigger.py` reads transcript, identifies edit to `GEMINI.md`, and runs `memory-pusher-jetski` agent (or script directly).
5.  **Sync**: `memory-pusher-jetski` commits and pushes changes to GitHub.

## Error Handling
*   Scripts should log failures to `/tmp/` logs to aid debugging without failing the main agent loop interactively.
*   Git failures (e.g., network issues) will be ignored or logged as warnings, allowing local work to continue.

## Testing
*   Verify `hooks.json` is recognized by Jetski.
*   Verify `memory-pull.sh` throttles correctly.
*   Verify `memory_push_trigger.py` correctly parses the transcript and triggers push only on `GEMINI.md` edits.
