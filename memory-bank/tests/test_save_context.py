import unittest
import sys
import os
import json
import io
from unittest.mock import patch, MagicMock

# Insert scripts folder to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

class TestSaveContext(unittest.TestCase):
    @patch('save_context.send_generation_request')
    def test_save_context_parses_transcript_and_posts_correctly(self, mock_post):
        # Setup dummy transcript file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dummy_transcript = os.path.join(base_dir, 'tests', 'dummy_transcript.jsonl')
        os.makedirs(os.path.dirname(dummy_transcript), exist_ok=True)
        
        with open(dummy_transcript, 'w') as f:
            f.write(json.dumps({"type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "I prefer vanilla CSS."}) + "\n")
            f.write(json.dumps({"type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Understood, using vanilla CSS."}) + "\n")

        mock_stdin = json.dumps({"transcriptPath": dummy_transcript, "workspacePaths": ["/dummy/root"]})
        
        with patch('sys.stdin', io.StringIO(mock_stdin)):
            import save_context
            save_context.run()

        # Clean up
        if os.path.exists(dummy_transcript):
            os.remove(dummy_transcript)

        self.assertTrue(mock_post.called)
        # 6th argument is events (index 5)
        history = mock_post.call_args[0][5]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "USER")
        self.assertEqual(history[1]["role"], "AGENT")

    @patch('save_context.send_generation_request')
    def test_save_context_handles_corrupted_transcript_lines(self, mock_post):
        # Setup dummy transcript file with a corrupted line
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dummy_transcript = os.path.join(base_dir, 'tests', 'dummy_transcript_corrupted.jsonl')
        os.makedirs(os.path.dirname(dummy_transcript), exist_ok=True)
        
        with open(dummy_transcript, 'w') as f:
            f.write(json.dumps({"type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "I prefer vanilla CSS."}) + "\n")
            f.write("{invalid_json_here}\n")  # Corrupted line
            f.write(json.dumps({"type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Understood, using vanilla CSS."}) + "\n")

        mock_stdin = json.dumps({"transcriptPath": dummy_transcript, "workspacePaths": ["/dummy/root"]})
        
        with patch('sys.stdin', io.StringIO(mock_stdin)):
            import save_context
            save_context.run()

        # Clean up
        if os.path.exists(dummy_transcript):
            os.remove(dummy_transcript)

        self.assertTrue(mock_post.called)
        # 6th argument is events (index 5)
        history = mock_post.call_args[0][5]
        # Should skip the corrupted line and successfully parse the other two lines
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "USER")
        self.assertEqual(history[1]["role"], "AGENT")
