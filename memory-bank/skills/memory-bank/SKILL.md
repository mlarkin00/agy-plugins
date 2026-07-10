---
name: gcp-memory-bank-tool
description: Use this skill to register and interact with manual fact retention on GCP Memory Bank.
---

# GCP Memory Bank Manual Tool Definition

This skill registers the `gcp_save_important_fact` tool directly in the model execution environment.

## Tool Schema: `gcp_save_important_fact`

- **Name**: `gcp_save_important_fact`
- **Description**: Saves a high-priority, persistent fact to the long-term Memory Bank. Use this immediately when the user shares an explicit permanent preference.
- **Parameters**:
  - `fact` (string, required): The precise fact to persist.
  - `scope` (string, required): "global" or "project". MUST be "global" by default. Only use "project" if the user explicitly asks for a "project-level" or "project-scoped" memory.

## Tool Implementation Detail

When executed, the tool triggers a post request to GCP `memories` API:
`POST https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/reasoningEngines/{engine_id}/memories`
Using identity scope keys resolved from standard ADC.
