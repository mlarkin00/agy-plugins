# Design: Adding Evals to Jetski Memory Skills

- **Date**: 2026-05-19
- **Status**: Proposed
- **Author**: Jetski

## Goal

Add evaluation sets to `add-memory`, `uninstall-memory`, and `verify-memory` skills to comply with the Agent Skills Specification (v1.1), specifically the requirement to have an `evals/` directory with standardized test queries.

## Proposed Changes

Create an `evals/` directory inside each skill folder and a `evals.json` file inside it. Each file will contain 10 cases (5 positive triggers, 5 near-misses).

### Component: `skills/add-memory`

#### [NEW] `skills/add-memory/evals/evals.json`

```json
[
  {
    "prompt": "Remember that I prefer using tabs for indentation.",
    "trap": "The agent might try to search memory or ask for confirmation instead of saving it immediately.",
    "assertions": [
      "The agent invokes the `add-memory` skill.",
      "The agent does not ask for confirmation."
    ]
  },
  {
    "prompt": "Save to memory: The project deadline is June 1st.",
    "trap": "The agent might just acknowledge instead of saving.",
    "assertions": [
      "The agent invokes the `add-memory` skill."
    ]
  },
  {
    "prompt": "Add to long-term memory that my role is Tech Lead.",
    "trap": "The agent might ask which file to save to.",
    "assertions": [
      "The agent invokes the `add-memory` skill."
    ]
  },
  {
    "prompt": "Keep in mind that we don't use TDD in this repo.",
    "trap": "The agent might argue about TDD benefits.",
    "assertions": [
      "The agent invokes the `add-memory` skill."
    ]
  },
  {
    "prompt": "Record this preference: I like dark mode.",
    "trap": "The agent might ignore it as a trivial preference.",
    "assertions": [
      "The agent invokes the `add-memory` skill."
    ]
  },
  {
    "prompt": "What did I tell you to remember?",
    "trap": "The agent might try to add this question to memory.",
    "assertions": [
      "The agent does NOT invoke the `add-memory` skill.",
      "The agent attempts to read or search memory."
    ]
  },
  {
    "prompt": "I remember reading about this in the docs.",
    "trap": "The agent might try to save this statement.",
    "assertions": [
      "The agent does NOT invoke the `add-memory` skill."
    ]
  },
  {
    "prompt": "Do you remember my name?",
    "trap": "The agent might try to save this query.",
    "assertions": [
      "The agent does NOT invoke the `add-memory` skill.",
      "The agent attempts to answer the question from memory."
    ]
  },
  {
    "prompt": "Forget what I said about Python.",
    "trap": "The agent might try to add a memory about forgetting.",
    "assertions": [
      "The agent does NOT invoke the `add-memory` skill.",
      "The agent attempts to remove or update the memory."
    ]
  },
  {
    "prompt": "Can you check if the memory file exists?",
    "trap": "The agent might try to save this request.",
    "assertions": [
      "The agent does NOT invoke the `add-memory` skill.",
      "The agent checks the filesystem."
    ]
  }
]
```

### Component: `skills/verify-memory`

#### [NEW] `skills/verify-memory/evals/evals.json`

```json
[
  {
    "prompt": "Check memory health.",
    "trap": "The agent might just say it's fine without checking.",
    "assertions": [
      "The agent invokes the `verify-memory` skill."
    ]
  },
  {
    "prompt": "Is the memory system working?",
    "trap": "The agent might answer based on recent success instead of checking.",
    "assertions": [
      "The agent invokes the `verify-memory` skill."
    ]
  },
  {
    "prompt": "Verify my memory is intact.",
    "trap": "The agent might ask what memory should contain.",
    "assertions": [
      "The agent invokes the `verify-memory` skill."
    ]
  },
  {
    "prompt": "Run the memory health check.",
    "trap": "The agent might look for a different script.",
    "assertions": [
      "The agent invokes the `verify-memory` skill."
    ]
  },
  {
    "prompt": "Test if memory is saving correctly.",
    "trap": "The agent might try to save a test memory instead of running verification.",
    "assertions": [
      "The agent invokes the `verify-memory` skill."
    ]
  },
  {
    "prompt": "Save this to memory.",
    "trap": "The agent might run verification instead of saving.",
    "assertions": [
      "The agent does NOT invoke the `verify-memory` skill.",
      "The agent invokes `add-memory`."
    ]
  },
  {
    "prompt": "What is currently in my memory?",
    "trap": "The agent might run verification to check content.",
    "assertions": [
      "The agent does NOT invoke the `verify-memory` skill.",
      "The agent reads memory file."
    ]
  },
  {
    "prompt": "How does the memory system work?",
    "trap": "The agent might run verification to see how it works.",
    "assertions": [
      "The agent does NOT invoke the `verify-memory` skill.",
      "The agent explains the system."
    ]
  },
  {
    "prompt": "Uninstall the memory plugin.",
    "trap": "The agent might run verification before uninstalling.",
    "assertions": [
      "The agent does NOT invoke the `verify-memory` skill.",
      "The agent invokes `uninstall-memory`."
    ]
  },
  {
    "prompt": "Clear my memory.",
    "trap": "The agent might run verification after clearing or instead of clearing.",
    "assertions": [
      "The agent does NOT invoke the `verify-memory` skill."
    ]
  }
]
```

### Component: `skills/uninstall-memory`

#### [NEW] `skills/uninstall-memory/evals/evals.json`

```json
[
  {
    "prompt": "Uninstall the memory plugin.",
    "trap": "The agent might ask if I'm sure instead of proceeding or offering to proceed.",
    "assertions": [
      "The agent invokes the `uninstall-memory` skill."
    ]
  },
  {
    "prompt": "Remove the agent-memory extension.",
    "trap": "The agent might not recognize 'extension' as 'plugin'.",
    "assertions": [
      "The agent invokes the `uninstall-memory` skill."
    ]
  },
  {
    "prompt": "Clean up the memory setup.",
    "trap": "The agent might just delete files instead of running the uninstall skill.",
    "assertions": [
      "The agent invokes the `uninstall-memory` skill."
    ]
  },
  {
    "prompt": "I want to remove the memory system.",
    "trap": "The agent might ask for confirmation.",
    "assertions": [
      "The agent invokes the `uninstall-memory` skill."
    ]
  },
  {
    "prompt": "Delete the memory plugin.",
    "trap": "The agent might just delete the directory.",
    "assertions": [
      "The agent invokes the `uninstall-memory` skill."
    ]
  },
  {
    "prompt": "How do I install the memory plugin?",
    "trap": "The agent might try to uninstall it first.",
    "assertions": [
      "The agent does NOT invoke the `uninstall-memory` skill.",
      "The agent provides installation instructions."
    ]
  },
  {
    "prompt": "Is the memory plugin installed?",
    "trap": "The agent might try to uninstall it to check.",
    "assertions": [
      "The agent does NOT invoke the `uninstall-memory` skill.",
      "The agent checks installation status."
    ]
  },
  {
    "prompt": "Check memory health.",
    "trap": "The agent might try to uninstall it if it's unhealthy.",
    "assertions": [
      "The agent does NOT invoke the `uninstall-memory` skill.",
      "The agent invokes `verify-memory`."
    ]
  },
  {
    "prompt": "Update the memory plugin.",
    "trap": "The agent might try to uninstall and reinstall.",
    "assertions": [
      "The agent does NOT invoke the `uninstall-memory` skill."
    ]
  },
  {
    "prompt": "Disable the memory plugin temporarily.",
    "trap": "The agent might uninstall it instead of disabling.",
    "assertions": [
      "The agent does NOT invoke the `uninstall-memory` skill."
    ]
  }
]
```

## Verification Plan

1.  Verify that the `evals.json` files are created in the correct directories.
2.  Verify that the JSON files are valid JSON.
