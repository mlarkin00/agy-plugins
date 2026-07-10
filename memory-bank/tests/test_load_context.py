import unittest
import sys
import os
import json
import io
from unittest.mock import patch, MagicMock

# Insert scripts folder to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

class TestLoadContext(unittest.TestCase):
    @patch('load_context.query_memory_bank')
    def test_load_context_prints_contract_compliant_json(self, mock_query):
        mock_query.return_value = ["Standard CSS only.", "Max pods 10."]
        
        # Simulate running main logic and capturing stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        # Simulate stdin JSON
        mock_stdin = '{"workspacePaths": ["/dummy/root"]}'
        
        with patch('sys.stdin', io.StringIO(mock_stdin)):
            import load_context
            load_context.run()
            
        sys.stdout = sys.__stdout__
        output = json.loads(captured_output.getvalue())
        self.assertIn("injectSteps", output)
        self.assertTrue(len(output["injectSteps"]) > 0)
        self.assertIn("ephemeralMessage", output["injectSteps"][0])
        self.assertIn("Standard CSS only.", output["injectSteps"][0]["ephemeralMessage"])

    @patch('load_context.query_memory_bank')
    def test_load_context_escapes_xml_entities(self, mock_query):
        mock_query.return_value = ["Standard CSS & HTML.", "Max pods < 10."]
        
        captured_output = io.StringIO()
        sys.stdout = captured_output
        mock_stdin = '{"workspacePaths": ["/dummy/root"]}'
        
        with patch('sys.stdin', io.StringIO(mock_stdin)):
            import load_context
            load_context.run()
            
        sys.stdout = sys.__stdout__
        output = json.loads(captured_output.getvalue())
        ephemeral = output["injectSteps"][0]["ephemeralMessage"]
        
        # Verify that raw `<` and `&` are properly escaped
        self.assertIn("Standard CSS &amp; HTML.", ephemeral)
        self.assertIn("Max pods &lt; 10.", ephemeral)
