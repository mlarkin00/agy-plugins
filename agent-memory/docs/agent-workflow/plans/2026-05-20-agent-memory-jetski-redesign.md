# Agent Memory Jetski Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use agent-workflow:subagent-driven-development (recommended) or agent-workflow:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the `agent-memory-jetski` plugin to work with Jetski hooks and remove reliance on symlinks and external scripts in `~/.gemini/`.

**Architecture:** Use `hooks.json` for event mapping (`PreInvocation` and `PostToolUse`). Update agent configs to use relative paths. Update scripts to handle Jetski specific hook inputs and throttling.

**Tech Stack:** JSON, YAML, Bash, Python.

---

### Task 1: Create Hooks Configuration

**Files:**
- Create: `hooks.json`

- [ ] **Step 1: Create `hooks.json`**
  Create the file at the root of the plugin directory with the following content:
  ```json
  {
    "agent-memory-pull": {
      "PreInvocation": [
        {
          "type": "command",
          "command": "./scripts/memory-pull.sh"
        }
      ]
    },
    "agent-memory-push": {
      "PostToolUse": [
        {
          "type": "command",
          "command": "python3 ./scripts/memory_push_trigger.py"
        }
      ]
    }
  }
  ```

- [ ] **Step 2: Verify JSON validity**
  Run: `python3 -m json.tool hooks.json > /dev/null`
  Expected: No output, exit code 0.

- [ ] **Step 3: Commit**
  Run: `git add hooks.json && git commit -m "feat: add hooks.json for Jetski"`

---

### Task 2: Update Agent Configurations

**Files:**
- Modify: `agents/bootstrap-memory-jetski/config.yaml`
- Modify: `agents/memory-puller-jetski/config.yaml`
- Modify: `agents/memory-pusher-jetski/config.yaml`

- [ ] **Step 1: Update `bootstrap-memory-jetski/config.yaml`**
  Remove Step 6 (install script symlinks) and update Step 7 to use `./scripts/verify-memory-jetski.sh`.
  
- [ ] **Step 2: Update `memory-puller-jetski/config.yaml`**
  Change command to `bash ./scripts/memory-pull.sh`.

- [ ] **Step 3: Update `memory-pusher-jetski/config.yaml`**
  Change command to `bash ./scripts/memory-push.sh`.

- [ ] **Step 4: Verify YAML validity**
  Run: `python3 -c "import yaml; yaml.safe_load(open('agents/bootstrap-memory-jetski/config.yaml'))"` (repeat for others).
  Expected: No output, exit code 0.

- [ ] **Step 5: Commit**
  Run: `git add agents/ && git commit -m "refactor: update agent configs to use relative paths"`

---

### Task 3: Update `scripts/memory-pull.sh`

**Files:**
- Modify: `scripts/memory-pull.sh`

- [ ] **Step 1: Add throttling logic**
  Add the following bash code to the top of the file:
  ```bash
  TIMESTAMP_FILE="/tmp/jetski-memory-pull-timestamp"
  CURRENT_TIME=$(date +%s)

  if [[ -f "$TIMESTAMP_FILE" ]]; then
    LAST_PULL=$(cat "$TIMESTAMP_FILE")
    if (( CURRENT_TIME - LAST_PULL < 300 )); then
      echo "[memory-pull] SKIP: pulled recently" >&2
      exit 0
    fi
  fi
  
  # Existing git logic...
  
  echo "$CURRENT_TIME" > "$TIMESTAMP_FILE"
  ```

- [ ] **Step 2: Test throttling**
  Run: `bash scripts/memory-pull.sh` (should pull or skip if recent). Run again immediately.
  Expected: Second run should output "[memory-pull] SKIP: pulled recently".

- [ ] **Step 3: Commit**
  Run: `git add scripts/memory-pull.sh && git commit -m "feat: add throttling to memory-pull.sh"`

---

### Task 4: Update `scripts/memory_push_trigger.py`

**Files:**
- Modify: `scripts/memory_push_trigger.py`

- [ ] **Step 1: Write failing test**
  Create `tests/test_memory_push_trigger.py` with a test that checks if it reads the transcript correctly.
  
- [ ] **Step 2: Run test to verify failure**
  Run: `pytest tests/test_memory_push_trigger.py`
  Expected: FAIL

- [ ] **Step 3: Implement transcript reading**
  Rewrite `scripts/memory_push_trigger.py` to read `transcriptPath` from stdin and find the tool call in the transcript.

- [ ] **Step 4: Run test to verify pass**
  Run: `pytest tests/test_memory_push_trigger.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run: `git add scripts/memory_push_trigger.py tests/test_memory_push_trigger.py && git commit -m "feat: update memory_push_trigger to read transcript"`

---

### Task 5: Cleanup

**Files:**
- Delete: `scripts/install-symlinks-jetski.sh`

- [ ] **Step 1: Delete script**
  Run: `rm scripts/install-symlinks-jetski.sh`

- [ ] **Step 2: Commit**
  Run: `git rm scripts/install-symlinks-jetski.sh && git commit -m "cleanup: remove install-symlinks-jetski.sh"`
