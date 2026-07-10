# GCP Memory Bank Plugin

This plugin integrates long-term memory for agents using the Google Cloud Platform (GCP) Vertex AI Reasoning Engine Memory Bank. It provides agents with persistent, scope-aware memory storage (both global and project-level) that survives across individual sessions.

## Architecture

The plugin is designed to run automatically as part of the agent's lifecycle, with explicit skills available for manual intervention.

### Automatic Lifecycle Hooks
The core automation is driven by hook configurations defined in `hooks.json`:
- **`PreInvocation` Hook (`load_context.py`)**: Runs immediately before the agent starts a session. It securely authenticates via Application Default Credentials (ADC), queries the GCP Memory Bank for both global facts and facts specific to the current workspace, and injects them directly into the agent's context.
- **`Stop` Hooks (`save_context.py` & `sidecar_consolidate.py`)**: Triggered when the agent's work session ends. These run asynchronously to process new information learned during the session, persist important facts to GCP, and consolidate or deduplicate overlapping memory entries.

### Backend Storage
Memory is stored remotely on Google Cloud, utilizing the `aiplatform.googleapis.com` API (specifically Vertex AI Reasoning Engine `memories` endpoints). This ensures the context is securely backed up and not dependent on local markdown state files.

## Features

- **Scope Awareness**: Supports saving facts with explicit scopes:
  - `global`: For user preferences or overarching rules (e.g., "always use python 3").
  - `project`: For workspace-specific context (e.g., "this repository uses FastAPI").
- **Automatic Context Injection**: Agents wake up already knowing important context, saving tokens and repetitive prompting.
- **Background Consolidation**: Prevents memory bloat by running cleanup jobs when the agent is idle.
- **Manual Control Skills**: Includes skills for direct memory management when needed.

## Components & Skills

Agents have access to several explicit skills (located in the `skills/` directory) to manage memory:
- **`memory-bank`**: Registers a tool to instantly save high-priority facts to the GCP Memory Bank.
- **`memories-list`**: Lists all memories stored, filterable by scope.
- **`memories-update`**: Edits existing facts.
- **`memories-delete`**: Removes facts that are no longer relevant.

## Installation & Configuration

1. **Enable the Plugin**:
   Ensure this plugin directory is placed within your agent's active plugins directory.

2. **Authenticate with GCP**:
   The plugin relies strictly on Application Default Credentials (ADC). You must authenticate your local environment with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```
   *Note: Ensure the authenticated account has the necessary permissions to access Vertex AI Reasoning Engine endpoints in your target GCP project.*

3. **Verify Hooks**:
   The `hooks.json` automatically wires the required scripts to the `PreInvocation` and `Stop` lifecycle events. No additional manual wiring is required.
