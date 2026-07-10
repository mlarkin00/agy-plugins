---
name: memories-list
description: List all memories stored in the GCP Reasoning Engine Memory Bank, with options to view the entire bank or filter to the current scope.
---

# Listing GCP Memory Bank Memories

This skill defines instructions and tools to list all stored long-term memories from the live GCP Reasoning Engine Memory Bank.

## Tool Schema: `gcp_list_memories`

- **Name**: `gcp_list_memories`
- **Description**: Retrieves and lists memories currently stored in the GCP Memory Bank.
- **Parameters**:
  - `scope` (string, optional): "current" (default) to list global and current project memories, or "all" to list all memories regardless of scope.

## Steps for Agents to Perform List

1. Call the `gcp_list_memories` tool or run `python3 ./scripts/list_memories.py`.
2. Format and display the results beautifully to the user (e.g., in a clean Markdown table with ID, Scope, and Fact Content).
