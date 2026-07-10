import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

class TestMemoryPushTrigger(unittest.TestCase):
    @patch('scripts.memory_push_trigger.subprocess.run')
    @patch('sys.stdin', new_callable=io.StringIO)
    @patch('scripts.memory_push_trigger.sys.exit')
    def test_trigger_on_memory_edit(self, mock_exit, mock_stdin, mock_run):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as temp_file:
            transcript_path = temp_file.name
            temp_file.write(json.dumps({
                "step_index": 0,
                "type": "TOOL_USE",
                "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": os.path.expanduser("~/.gemini/GEMINI.md")}}]
            }) + "\n")
        self.addCleanup(os.remove, transcript_path)
            
        mock_stdin.write(json.dumps({
            "stepIdx": 0,
            "transcriptPath": transcript_path
        }))
        mock_stdin.seek(0)
        
        from scripts.memory_push_trigger import main
        main()
        
        mock_run.assert_called_once_with(["/google/bin/releases/jetski-devs/tools/cli", "agents", "run", "memory-pusher"])
        mock_exit.assert_not_called()
        
    @patch('scripts.memory_push_trigger.subprocess.run')
    @patch('sys.stdin', new_callable=io.StringIO)
    @patch('scripts.memory_push_trigger.sys.exit')
    def test_no_trigger_on_other_file(self, mock_exit, mock_stdin, mock_run):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as temp_file:
            transcript_path = temp_file.name
            temp_file.write(json.dumps({
                "step_index": 0,
                "type": "TOOL_USE",
                "tool_calls": [{"name": "write_to_file", "args": {"TargetFile": "/tmp/other.txt"}}]
            }) + "\n")
        self.addCleanup(os.remove, transcript_path)
            
        mock_stdin.write(json.dumps({
            "stepIdx": 0,
            "transcriptPath": transcript_path
        }))
        mock_stdin.seek(0)
        
        from scripts.memory_push_trigger import main
        main()
        
        mock_run.assert_not_called()
        mock_exit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
