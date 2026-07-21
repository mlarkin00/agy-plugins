# TODO

## P0 — Address Immediately

_(none)_

## P1 — Important / Unblocking

- [ ] **[P1]** Verify and fix `agent-memory`'s `PostToolUse` hook, which almost certainly never fires. `agent-memory/hooks.json` declares `agent-memory-push.PostToolUse` in the flat `{"type": "command", ...}` form. Testing against `agy` 1.1.5 (2026-07-21) showed the flat form installs and reports `hooks: N processed` but never executes; only the nested `{"matcher": ..., "hooks": [...]}` form fires. If confirmed, memory pushes have been silently dead — the plugin reports healthy and does nothing. Fix by nesting the handler:

  ```json
  "PostToolUse": [
    { "matcher": "", "hooks": [
      { "type": "command", "command": "python3 ./scripts/memory_push_trigger.py", "timeout": 10 } ] } ]
  ```

  Confirm with a live run before and after — a passing install is not evidence of a firing hook. Escalate to P0 if the failure is confirmed, since it silently breaks the plugin's core purpose.

- [ ] **[P1]** Audit the `PreInvocation` and `Stop` handlers in `agent-memory` and `memory-bank`, which use the same flat form. Unlike `PostToolUse`, it is **not** established that nesting fixes these: in `agy --print` mode, neither form of `PreInvocation`, `PostInvocation`, or `Stop` fired at all during testing. Determine whether these events fire only in interactive mode; if they never fire, move the work to a scheduled sidecar as `active-skills` now does for its usage flush.

- [ ] **[P1]** Remove the hardcoded Google-internal binary path from this **public** repo — `/google/bin/releases/jetski-devs/tools/cli` appears in `agent-memory/scripts/memory_push_trigger.py:60` and `agent-memory/tests/test_memory_push_trigger.py:31`. Resolve the CLI from `PATH` or an env var instead.

## P2 — Nice-to-Have

- [ ] **[P2]** Consider adding a `Stop`-block guard to any plugin that also uses `PostToolUse`. In `agy` 1.1.5 a `Stop` block anywhere in a plugin's `hooks.json` silently prevents `PostToolUse` from firing, even when declared under a separate hook name. See `mlarkin00/active-skills` `AGENTS.md` for the full finding.

- [ ] **[P2]** Once `mlarkin00/active-skills` is cut over, retire this repo's vendored `active-skills/` copy and its `sync-active-skills.yml`, and reference the source repo directly — pending confirmation that Antigravity supports external plugin sources.
