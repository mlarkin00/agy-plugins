import unittest
import sys
import os
import json
import io
from unittest.mock import patch, MagicMock

# Insert scripts folder to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

class TestMemoryOps(unittest.TestCase):
    @patch('list_memories.list_memories')
    @patch('list_memories.resolve_user_id')
    @patch('list_memories.resolve_project_id')
    def test_list_memories_current_scope(self, mock_project, mock_user, mock_list):
        mock_user.return_value = "user_abc"
        mock_project.return_value = "project_xyz"
        mock_list.return_value = [
            {
                "name": "projects/123/locations/us-central1/reasoningEngines/123/memories/m1",
                "fact": "Fact 1",
                "scope": {"user": "user_abc", "project": "project_xyz"},
                "createTime": "2026-06-10T20:00:00Z"
            },
            {
                "name": "projects/123/locations/us-central1/reasoningEngines/123/memories/m2",
                "fact": "Fact 2",
                "scope": {"user": "user_other", "project": "project_xyz"},
                "createTime": "2026-06-10T20:01:00Z"
            }
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        import list_memories
        with patch('sys.argv', ['list_memories.py', '--scope', 'current']):
            list_memories.main()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Fact 1", output)
        self.assertNotIn("Fact 2", output)

    @patch('list_memories.list_memories')
    @patch('list_memories.resolve_user_id')
    @patch('list_memories.resolve_project_id')
    def test_list_memories_all_scope(self, mock_project, mock_user, mock_list):
        mock_user.return_value = "user_abc"
        mock_project.return_value = "project_xyz"
        mock_list.return_value = [
            {
                "name": "projects/123/locations/us-central1/reasoningEngines/123/memories/m1",
                "fact": "Fact 1",
                "scope": {"user": "user_abc", "project": "project_xyz"},
                "createTime": "2026-06-10T20:00:00Z"
            },
            {
                "name": "projects/123/locations/us-central1/reasoningEngines/123/memories/m2",
                "fact": "Fact 2",
                "scope": {"user": "user_other", "project": "project_xyz"},
                "createTime": "2026-06-10T20:01:00Z"
            }
        ]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        import list_memories
        with patch('sys.argv', ['list_memories.py', '--scope', 'all']):
            list_memories.main()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Fact 1", output)
        self.assertIn("Fact 2", output)

    @patch('delete_memory.delete_memory')
    def test_delete_memory_success(self, mock_delete):
        # Simulate synchronous direct empty response
        mock_delete.return_value = {}

        captured_output = io.StringIO()
        sys.stdout = captured_output

        import delete_memory
        with patch('sys.argv', ['delete_memory.py', 'm1']):
            delete_memory.main()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Successfully deleted memory 'm1'", output)

    @patch('update_memory.update_memory')
    def test_update_memory_success(self, mock_update):
        # Simulate synchronous direct resource response
        mock_update.return_value = {"name": "m1", "fact": "New Fact"}

        captured_output = io.StringIO()
        sys.stdout = captured_output

        import update_memory
        with patch('sys.argv', ['update_memory.py', 'm1', 'New Fact']):
            update_memory.main()

        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Successfully updated memory 'm1'", output)

if __name__ == '__main__':
    unittest.main()
