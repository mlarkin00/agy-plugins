import json
import os
import unittest

class TestPluginMetadata(unittest.TestCase):
    def test_metadata_and_hooks_exist_and_are_valid_json(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        plugin_path = os.path.join(base_dir, 'plugin.json')
        hooks_path = os.path.join(base_dir, 'hooks.json')

        self.assertTrue(os.path.exists(plugin_path), "plugin.json is missing")
        self.assertTrue(os.path.exists(hooks_path), "hooks.json is missing")

        with open(plugin_path, 'r') as f:
            plugin_data = json.load(f)
            self.assertEqual(plugin_data.get('name'), 'gcp-memory-bank')

        with open(hooks_path, 'r') as f:
            hooks_data = json.load(f)
            self.assertIn('gcp-memory-bank-loader', hooks_data)
            self.assertIn('PreInvocation', hooks_data['gcp-memory-bank-loader'])
