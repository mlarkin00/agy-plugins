import unittest
import sys
import os

# Insert scripts folder to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

class TestScopeResolution(unittest.TestCase):
    def test_git_url_normalization_ssh_and_https_match(self):
        from resolve_scope import normalize_git_url
        urls = [
            "git@github.com:mlarkin00/agent-skills.git",
            "https://github.com/mlarkin00/agent-skills.git",
            "ssh://git@github.com/mlarkin00/agent-skills",
            "http://github.com/mlarkin00/agent-skills"
        ]
        normalized = [normalize_git_url(url) for url in urls]
        first = normalized[0]
        self.assertEqual(first, "github.com/mlarkin00/agent-skills")
        for norm in normalized:
            self.assertEqual(norm, first)

    def test_hash_string_output_format(self):
        from resolve_scope import hash_string
        val = hash_string("test")
        self.assertTrue(val.startswith("sha256:"))
        self.assertEqual(len(val), 64 + 7) # "sha256:" prefix + 64 hex characters
