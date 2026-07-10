import unittest
import sys
import os
import json
import time
import io
from unittest.mock import patch, MagicMock

# Insert scripts folder to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

class TestSidecarConsolidate(unittest.TestCase):
    @patch('sidecar_consolidate.get_state_file_path')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_gate_throttles_within_24_hours(self, mock_open, mock_exists, mock_state_path):
        import sidecar_consolidate
        mock_state_path.return_value = "/dummy/state.json"
        
        # State file exists
        mock_exists.return_value = True
        
        # Last run was 5 seconds ago
        state_data = {"last_run": time.time() - 5}
        mock_file = MagicMock()
        mock_file.read.return_value = json.dumps(state_data)
        mock_open.return_value.__enter__.return_value = mock_file
        
        self.assertFalse(sidecar_consolidate.should_run_sidecar(interval_seconds=86400))

    @patch('sidecar_consolidate.get_state_file_path')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_gate_allows_past_24_hours_or_if_no_state(self, mock_open, mock_exists, mock_state_path):
        import sidecar_consolidate
        mock_state_path.return_value = "/dummy/state.json"
        
        # Case A: State file doesn't exist -> should run
        mock_exists.return_value = False
        self.assertTrue(sidecar_consolidate.should_run_sidecar(interval_seconds=86400))

        # Case B: State exists but last run was 25 hours ago -> should run
        mock_exists.return_value = True
        state_data = {"last_run": time.time() - 90000} # 25 hours ago
        mock_file = MagicMock()
        mock_file.read.return_value = json.dumps(state_data)
        mock_open.return_value.__enter__.return_value = mock_file
        self.assertTrue(sidecar_consolidate.should_run_sidecar(interval_seconds=86400))

    @patch('os.path.exists')
    @patch('os.walk')
    @patch('builtins.open')
    def test_aggregate_transcripts_finds_and_decodes_correctly(self, mock_open, mock_walk, mock_exists):
        mock_exists.return_value = True
        import sidecar_consolidate
        
        # Mock os.walk structure
        mock_walk.return_value = [
            ("/brain/conv1/.system_generated/logs", [], ["transcript.jsonl"]),
            ("/brain/conv2/.system_generated/logs", [], ["transcript.jsonl"])
        ]
        
        # Simulate open content for different files
        file1_lines = [
            json.dumps({"type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "I prefer dark theme."}),
            json.dumps({"type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Applying dark theme."})
        ]
        file2_lines = [
            json.dumps({"type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "Restrict pods to 5."}),
            "{corrupted_json_here}",
            json.dumps({"type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Got it, pods capped."})
        ]
        
        def open_side_effect(filepath, *args, **kwargs):
            m = MagicMock()
            if "conv1" in filepath:
                m.__enter__.return_value = file1_lines
            elif "conv2" in filepath:
                m.__enter__.return_value = file2_lines
            else:
                m.__enter__.return_value = []
            return m
            
        mock_open.side_effect = open_side_effect
        
        events = sidecar_consolidate.aggregate_transcripts("/brain")
        self.assertEqual(len(events), 4) # skips corrupt line
        self.assertEqual(events[0]["role"], "USER")
        self.assertEqual(events[1]["role"], "AGENT")
        self.assertEqual(events[2]["role"], "USER")
        self.assertEqual(events[3]["role"], "AGENT")

    @patch('sidecar_consolidate.should_run_sidecar')
    @patch('sidecar_consolidate.aggregate_transcripts')
    @patch('sidecar_consolidate.resolve_user_id')
    @patch('sidecar_consolidate.resolve_project_id')
    @patch('sidecar_consolidate.save_state_timestamp')
    @patch('urllib.request.urlopen')
    def test_run_sends_api_request_and_updates_state(self, mock_urlopen, mock_save_state, mock_resolve_project, mock_resolve_user, mock_aggregate, mock_should_run):
        import sidecar_consolidate
        mock_should_run.return_value = True
        mock_aggregate.return_value = [{"role": "USER", "content": "I want TailwindCSS."}]
        mock_resolve_user.return_value = "user_hash_123"
        mock_resolve_project.return_value = "project_hash_456"
        
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        mock_stdin = json.dumps({"workspacePaths": ["/my/workspace/path"]})
        with patch('sys.stdin', io.StringIO(mock_stdin)):
            sidecar_consolidate.run()
            
        self.assertTrue(mock_urlopen.called)
        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.method, 'POST')
        self.assertEqual(req.full_url, 'https://us-central1-aiplatform.googleapis.com/v1beta1/projects/my-project/locations/us-central1/reasoningEngines/123/memories:generate')
        
        data = json.loads(req.data.decode('utf-8'))
        self.assertEqual(data["scope"]["user"], "user_hash_123")
        self.assertEqual(data["scope"]["project"], "project_hash_456")
        self.assertEqual(data["directContentsSource"]["events"][0]["role"], "USER")
        self.assertEqual(data["directContentsSource"]["events"][0]["content"], "I want TailwindCSS.")
        
        self.assertTrue(mock_save_state.called)

    @patch('sidecar_consolidate.list_memories')
    @patch('sidecar_consolidate.delete_memory')
    def test_deduplicate_memories_deletes_redundant_and_keeps_oldest(self, mock_delete, mock_list):
        import sidecar_consolidate
        
        # Setup mock duplicate memories
        mock_list.return_value = [
            {
                "name": "projects/my-project/locations/us-central1/reasoningEngines/123/memories/m1",
                "createTime": "2026-06-10T20:11:00Z",
                "scope": {"user": "userA", "project": "projA"},
                "fact": "Duplicate Fact"
            },
            {
                "name": "projects/my-project/locations/us-central1/reasoningEngines/123/memories/m2",
                "createTime": "2026-06-10T20:12:00Z",
                "scope": {"user": "userA", "project": "projA"},
                "fact": "duplicate fact  "  # slight whitespace/case difference
            },
            {
                "name": "projects/my-project/locations/us-central1/reasoningEngines/123/memories/m3",
                "createTime": "2026-06-10T20:10:00Z", # oldest duplicate
                "scope": {"user": "userA", "project": "projA"},
                "fact": "DUPLICATE FACT"
            },
            {
                "name": "projects/my-project/locations/us-central1/reasoningEngines/123/memories/m4",
                "createTime": "2026-06-10T20:15:00Z",
                "scope": {"user": "userA", "project": "projA"},
                "fact": "Unique Fact"
            }
        ]
        
        mock_delete.return_value = True
        
        sidecar_consolidate.deduplicate_memories("my-project", "us-central1", "123")
        
        # Verify delete was called for m1 and m2 (since m3 is oldest)
        self.assertEqual(mock_delete.call_count, 2)
        called_ids = [call_args[0][3] for call_args in mock_delete.call_args_list]
        self.assertIn("m1", called_ids)
        self.assertIn("m2", called_ids)
        self.assertNotIn("m3", called_ids)
        self.assertNotIn("m4", called_ids)


