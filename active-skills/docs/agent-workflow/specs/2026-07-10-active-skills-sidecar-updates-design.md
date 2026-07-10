# Spec: Active-Skills Plugin Update Checker Sidecar

This specification outlines the design and implementation of a daily update checker sidecar for the `active-skills` plugin in Antigravity.

## Goal
Add a sidecar to the `active-skills` plugin that runs once daily, checks the `mlarkin00/agy-plugins` GitHub repository to see if a newer version of the `active-skills` plugin is available, and logs the update status while persisting the state.

## Architecture & File Layout
The sidecar is fully self-contained within the `active-skills` plugin folder:

```text
active-skills/
├── plugin.json
├── sidecars/
│   └── check-updates/
│       ├── sidecar.json       # Sidecar configuration file
│       └── check_updates.py   # Self-contained Python update checker script
```

## Specification

### 1. Sidecar Configuration (`sidecar.json`)
The sidecar uses Antigravity's `"builtin": "schedule"` tool to run the update checker script daily at 12:00 PM (noon).

```json
{
  "description": "Checks for updates to active-skills plugin daily.",
  "builtin": "schedule",
  "args": [
    "0 12 * * *",
    "python3",
    "check_updates.py"
  ],
  "restart_policy": "on-failure"
}
```

### 2. Update Checker Script (`check_updates.py`)
A self-contained Python 3 script with zero external dependencies.

#### Logic:
1. **Find Plugin Manifest**:
   The script locates its parent plugin's manifest (`plugin.json`) relative to its execution directory: `../../plugin.json`.
2. **Read Current Version**:
   It parses the local version from `plugin.json` (under the key `"version"`).
3. **Fetch Remote Manifest**:
   Using Python's built-in `urllib.request` library, it fetches the remote manifest file:
   `https://raw.githubusercontent.com/mlarkin00/agy-plugins/main/active-skills/plugin.json`
4. **Compare Versions**:
   It compares semantic versions using integer tuple decomposition (e.g. `(0, 1, 4)` vs `(0, 1, 5)`) to support multi-digit segment comparisons correctly.
5. **Log Status**:
   - If an update is available: Prints `[UPDATE] A newer version of active-skills is available: local=X.Y.Z, remote=A.B.C`.
   - If up-to-date: Prints `[OK] active-skills is up-to-date (vX.Y.Z)`.
6. **Persist State**:
   It writes the results of the check to a `status.json` file in the sidecar's data directory. It uses the `ANTIGRAVITY_EXECUTABLE_DATA_DIR` environment variable if available, falling back to a local `data/` subdirectory.

   ```json
   {
     "last_checked": "2026-07-10T22:20:28Z",
     "local_version": "0.1.4",
     "remote_version": "0.1.5",
     "update_available": true
   }
   ```

## Verification & Testing Plan
1. **Local Test Execution**: Execute the Python script manually from its directory (`active-skills/sidecars/check-updates/`) and verify:
   - Correct parsing of local `../../plugin.json`.
   - Successful HTTP fetch of remote `plugin.json`.
   - Accurate version comparison logic (mocking local and remote versions).
   - Correct creation/update of `status.json` containing the status payload.
2. **Config Validation**: Validate that `sidecar.json` strictly adheres to the Antigravity sidecar schema.
