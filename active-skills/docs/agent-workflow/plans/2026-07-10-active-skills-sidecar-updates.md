# Active-Skills Update Checker Sidecar Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use agent-workflow:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a sidecar to the active-skills plugin that checks daily for updates to the `active-skills` plugin in the `mlarkin00/agy-plugins` GitHub repository.

**Architecture:** Create a `sidecars/check-updates/` folder with `sidecar.json` scheduling the check daily via Antigravity's `schedule` builtin. The check executes a self-contained Python script `check_updates.py` that reads the local version, fetches the remote version, logs results, and writes status JSON.

**Tech Stack:** Python 3 (with standard library `urllib`, `json`, `sys`, `os`, `datetime`), JSON, Shell.

---

### Task 1: Update Checker Script & Tests

**Files:**
- Create: `active-skills/sidecars/check-updates/check_updates.py`
- Create: `active-skills/tests/test_check_updates.py`

- [ ] **Step 1: Write the failing tests**
  Create the test suite that mocks `urllib.request.urlopen` and local file I/O to test the version comparison and JSON status generation.
  Create `active-skills/tests/test_check_updates.py`:
  ```python
  import os
  import sys
  import unittest
  from unittest.mock import patch, mock_open, MagicMock

  # Ensure sidecar path can be imported
  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../sidecars/check-updates')))

  class TestCheckUpdates(unittest.TestCase):
      @patch('urllib.request.urlopen')
      @patch('builtins.open')
      @patch('os.environ.get')
      def test_update_available(self, mock_env, mock_file, mock_urlopen):
          # Mock environment to provide data dir
          mock_env.return_value = '/tmp/sidecar_data'
          
          # Mock local plugin.json reading
          local_json = '{"name": "active-skills", "version": "0.1.4"}'
          # Mock remote plugin.json fetching
          remote_json = b'{"name": "active-skills", "version": "0.1.5"}'
          
          mock_file.return_value.__enter__.return_value.read.return_value = local_json
          
          mock_response = MagicMock()
          mock_response.read.return_value = remote_json
          mock_urlopen.return_value.__enter__.return_value = mock_response
          
          from check_updates import check_for_updates
          status = check_for_updates()
          
          self.assertTrue(status['update_available'])
          self.assertEqual(status['local_version'], '0.1.4')
          self.assertEqual(status['remote_version'], '0.1.5')

      @patch('urllib.request.urlopen')
      @patch('builtins.open')
      @patch('os.environ.get')
      def test_up_to_date(self, mock_env, mock_file, mock_urlopen):
          mock_env.return_value = '/tmp/sidecar_data'
          local_json = '{"name": "active-skills", "version": "0.1.4"}'
          remote_json = b'{"name": "active-skills", "version": "0.1.4"}'
          
          mock_file.return_value.__enter__.return_value.read.return_value = local_json
          
          mock_response = MagicMock()
          mock_response.read.return_value = remote_json
          mock_urlopen.return_value.__enter__.return_value = mock_response
          
          # Force reload or clean import
          if 'check_updates' in sys.modules:
              del sys.modules['check_updates']
          from check_updates import check_for_updates
          status = check_for_updates()
          
          self.assertFalse(status['update_available'])
          self.assertEqual(status['local_version'], '0.1.4')
          self.assertEqual(status['remote_version'], '0.1.4')

  if __name__ == '__main__':
      unittest.main()
  ```

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest active-skills/tests/test_check_updates.py`
  Expected: FAIL with `ModuleNotFoundError: No module named 'check_updates'`

- [ ] **Step 3: Write minimal implementation**
  Create `active-skills/sidecars/check-updates/check_updates.py`:
  ```python
  import os
  import sys
  import json
  import urllib.request
  from datetime import datetime

  def parse_version(v_str):
      try:
          return tuple(map(int, v_str.strip().split('.')))
      except ValueError:
          return (0, 0, 0)

  def check_for_updates():
      # 1. Locate and parse local plugin.json
      current_dir = os.path.dirname(os.path.abspath(__file__))
      local_path = os.path.abspath(os.path.join(current_dir, '../../plugin.json'))
      
      try:
          with open(local_path, 'r', encoding='utf-8') as f:
              local_manifest = json.load(f)
              local_version = local_manifest.get('version', '0.0.0')
      except Exception as e:
          print(f"Error reading local manifest: {e}", file=sys.stderr)
          local_version = '0.0.0'

      # 2. Fetch remote plugin.json
      remote_url = 'https://raw.githubusercontent.com/mlarkin00/agy-plugins/main/active-skills/plugin.json'
      try:
          req = urllib.request.Request(remote_url, headers={'User-Agent': 'Mozilla/5.0'})
          with urllib.request.urlopen(req, timeout=10) as response:
              remote_manifest = json.loads(response.read().decode('utf-8'))
              remote_version = remote_manifest.get('version', '0.0.0')
      except Exception as e:
          print(f"Error fetching remote manifest: {e}", file=sys.stderr)
          remote_version = '0.0.0'

      # 3. Compare versions
      update_available = parse_version(remote_version) > parse_version(local_version)

      if update_available:
          print(f"[UPDATE] A newer version of active-skills is available: local={local_version}, remote={remote_version}")
      else:
          print(f"[OK] active-skills is up-to-date (v{local_version})")

      # 4. Persist state
      status_data = {
          "last_checked": datetime.utcnow().isoformat() + "Z",
          "local_version": local_version,
          "remote_version": remote_version,
          "update_available": update_available
      }

      data_dir = os.environ.get('ANTIGRAVITY_EXECUTABLE_DATA_DIR')
      if not data_dir:
          data_dir = os.path.join(current_dir, 'data')
      
      try:
          os.makedirs(data_dir, exist_ok=True)
          status_path = os.path.join(data_dir, 'status.json')
          with open(status_path, 'w', encoding='utf-8') as f:
              json.dump(status_data, f, indent=2)
      except Exception as e:
          print(f"Error writing status.json: {e}", file=sys.stderr)

      return status_data

  if __name__ == '__main__':
      check_for_updates()
  ```

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 -m unittest active-skills/tests/test_check_updates.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add active-skills/sidecars/check-updates/check_updates.py active-skills/tests/test_check_updates.py
  git commit -m "feat(active-skills): add daily update checker python script and unit tests"
  ```

---

### Task 2: Configure Sidecar Definition

**Files:**
- Create: `active-skills/sidecars/check-updates/sidecar.json`

- [ ] **Step 1: Write sidecar.json configuration**
  Create `active-skills/sidecars/check-updates/sidecar.json`:
  ```json
  {
    "description": "Checks for updates to active-skills plugin daily.",
    "builtin": "schedule",
    "args": [
      "0 12 * * *",
      "python3",
      "check_updates.py"
    ],
    "restart_policy": "on-failure"
  }
  ```

- [ ] **Step 2: Run verification**
  Run a dry run of the script locally to make sure it doesn't fail:
  `python3 active-skills/sidecars/check-updates/check_updates.py`
  Verify that a `status.json` file gets written under `active-skills/sidecars/check-updates/data/status.json` and its contents are valid JSON.

- [ ] **Step 3: Commit**
  ```bash
  git add active-skills/sidecars/check-updates/sidecar.json
  git commit -m "feat(active-skills): add daily update checker sidecar configuration"
  ```
