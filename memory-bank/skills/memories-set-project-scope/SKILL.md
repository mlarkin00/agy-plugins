---
name: memories-set-project-scope
description: Re-scope an existing global memory to the current project in the GCP Reasoning Engine Memory Bank.
---

# Re-Scoping GCP Memory Bank Memories

This skill defines instructions and tools to re-scope a globally stored long-term memory so that it is only retained for the current project.

## Tool Schema: `gcp_set_project_scope`

- **Name**: `gcp_set_project_scope`
- **Description**: Re-scopes an existing memory from global to the current project scope.
- **Parameters**:
  - `memory_id` (string, required): The ID of the memory to re-scope (e.g., "1097192207997206528").

## Steps for Agents to Perform Re-Scope

1. Identify the unique Memory ID of the global memory to re-scope.
2. Call the `gcp_set_project_scope` tool or run `python3 ./scripts/set_project_scope.py [memory_id]`.
3. Inform the user of the successful re-scoping and note that the memory has been given a new ID.
