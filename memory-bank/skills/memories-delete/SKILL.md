---
name: memories-delete
description: Delete a specific memory by its ID from the GCP Reasoning Engine Memory Bank.
---

# Deleting GCP Memory Bank Memories

This skill defines instructions and tools to delete specific long-term memories by ID from the live GCP Reasoning Engine Memory Bank.

## Tool Schema: `gcp_delete_memory`

- **Name**: `gcp_delete_memory`
- **Description**: Deletes a specific memory from the GCP Memory Bank.
- **Parameters**:
  - `memory_id` (string, required): The ID of the memory to delete (e.g., "1097192207997206528").

## Steps for Agents to Perform Delete

1. Identify the unique Memory ID (usually retrieved from a list or search query).
2. Call the `gcp_delete_memory` tool or run `python3 ./scripts/delete_memory.py [memory_id]`.
3. Inform the user of the successful deletion.
