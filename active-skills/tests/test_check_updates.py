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
