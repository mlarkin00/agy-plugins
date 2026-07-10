import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Ensure scripts is in system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
from create_engine import build_payload, parse_operation_response

class TestCreateEngine(unittest.TestCase):
    def test_build_payload(self):
        payload = build_payload(
            display_name="Test Memory",
            description="Test Desc",
            project="test-project",
            location="us-west1"
        )
        self.assertEqual(payload["displayName"], "Test Memory")
        self.assertEqual(
            payload["contextSpec"]["memoryBankConfig"]["generationConfig"]["model"],
            "projects/test-project/locations/us-west1/publishers/google/models/gemini-3.5-flash"
        )

    def test_parse_operation_response_running(self):
        res = {"name": "operations/123", "done": False}
        done, engine_id = parse_operation_response(res)
        self.assertFalse(done)
        self.assertIsNone(engine_id)

    def test_parse_operation_response_done(self):
        res = {
            "name": "operations/123",
            "done": True,
            "response": {
                "name": "projects/test-proj/locations/us-west1/reasoningEngines/998877"
              }
        }
        done, engine_id = parse_operation_response(res)
        self.assertTrue(done)
        self.assertEqual(engine_id, "998877")

if __name__ == '__main__':
    unittest.main()
