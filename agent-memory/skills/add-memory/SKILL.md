---
name: add-memory-jetski
description: Use when the user says "remember that …", "save this to memory", "add to long-term memory", or otherwise explicitly asks for information to be persisted across sessions. Saves the memory immediately to the global GEMINI.md file.
---

Save the memory details provided by the user **immediately**. Do NOT ask for confirmation, clarification, or the user's permission — the invocation itself is the permission.

Memory file: `~/.gemini/GEMINI.md` (symlinked to `~/.agents/agent-memory/GEMINI.md`; writes here are committed and pushed to GitHub automatically by the AfterTool hook).

## Steps

### 1. Classify the memory

Pick the type that best fits the content:

| Type        | Use for                                                                                |
| ----------- | -------------------------------------------------------------------------------------- |
| `user`      | Facts about the user: role, preferences, responsibilities, domain knowledge            |
| `feedback`  | How to approach work: rules to follow, things to avoid, validated approaches to repeat |
| `project`   | Initiative/bug/incident state: who's doing what, why, deadlines, motivations           |
| `reference` | Pointers to external systems: Linear projects, Slack channels, dashboards, docs        |

### 2. Update GEMINI.md

Read `~/.gemini/GEMINI.md`. Append the new memory to the appropriate section or at the end. Use a clean, concise format.

Example:

```markdown
### <Type>: <Short Title>

<The memory content. Convert relative dates to absolute ISO dates.>
```

### 3. Confirm

Print one line to the user:

```
✓ Saved memory to GEMINI.md (<type>)
```

## Rules

- **No questions asked.**
- **The AfterTool hook handles git.** Do not manually `git add`, commit, or push.
