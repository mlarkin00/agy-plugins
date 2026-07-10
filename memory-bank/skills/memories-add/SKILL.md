---
name: memories-add
description: Add a new explicit memory fact to the GCP Reasoning Engine Memory Bank.
---

# Adding GCP Memory Bank Memories

This skill defines instructions and tools to add a new explicit long-term memory to the live GCP Reasoning Engine Memory Bank.

## Tool Schema: `gcp_add_memory`

- **Name**: `gcp_add_memory`
- **Description**: Adds a new explicit fact to the GCP Memory Bank.
- **Parameters**:
  - `fact` (string, required): The fact text to persist.
  - `scope` (string, optional): "global" or "project". MUST be "global" by default. Only use "project" if the user explicitly asks for a "project-level" or "project-scoped" memory.

## Steps for Agents to Perform Add

1. Ensure the user wants to persist an explicit fact.
2. Call the `gcp_add_memory` tool or run `python3 ./scripts/add_memory.py "[fact]" --scope [global|project]`.
3. Inform the user of the successful addition.
