# Agent Instructions

## Project Goal
Integrate long-term memory for agents using the GCP Agent Platform Memory Bank, supporting global and project-level scopes. All designs, plans, and implementations MUST be in line with this goal.

## Project Context
This is a Python plugin for agent-skills providing GCP Memory Bank integration. It registers a tool for saving facts manually and uses lifecycle hooks (`PreInvocation` and `Stop`) to automatically load and consolidate context across sessions.

## Operational Commands
- Format/Lint: Ensure Python files are clean before committing.
- Run tests: Use `pytest` in the `tests/` directory if tests exist.

## Style & Conventions
- Language: Python 3
- Dependencies: Standard libraries and Google Cloud Vertex AI/Reasoning Engine SDKs.
- Avoid large monolithic scripts; keep scripts under `scripts/` focused on a single responsibility (e.g. `load_context.py`, `save_context.py`).

## Architecture & Constraints
- Hooks: `hooks.json` maps `PreInvocation` to `load_context.py` and `Stop` to `save_context.py` and `sidecar_consolidate.py`.
- Skills: Memory management skills reside in `skills/`.
- Scoping: The default scope for all memories MUST be `global`. Only use `project` scope when the user explicitly requests project-specific memory.
- Configuration: Read from `plugin.json` via `scripts/config.py` (falls back to `GCP_PROJECT`, `GCP_LOCATION`, `GCP_REASONING_ENGINE`).
- MUST use Application Default Credentials (ADC) for authentication.
