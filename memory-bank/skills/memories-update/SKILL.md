---
name: memories-update
description: Update an existing memory's fact content by ID in the GCP Reasoning Engine Memory Bank.
---

# Updating GCP Memory Bank Memories

This skill defines instructions and tools to update/patch the fact content of an existing long-term memory in the live GCP Reasoning Engine Memory Bank.

## Tool Schema: `gcp_update_memory`

- **Name**: `gcp_update_memory`
- **Description**: Updates the text content of a specific memory in the GCP Memory Bank.
- **Parameters**:
  - `memory_id` (string, required): The ID of the memory to update (e.g., "1097192207997206528").
  - `fact` (string, required): The new fact text/instructions.

## Steps for Agents to Perform Update

1. Identify the unique Memory ID (usually retrieved from a list or search query).
2. Call the `gcp_update_memory` tool or run `python3 ./scripts/update_memory.py [memory_id] "[new_fact]"`.
3. Inform the user of the successful update.
