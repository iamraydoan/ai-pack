import unittest
import os
import tempfile
import shutil
from ai_pack import GitignoreMatcher

class TestGitignoreMatcher(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_standard_ignores(self):
        matcher = GitignoreMatcher(self.test_dir)
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "node_modules", "lodash", "index.js")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "src", "__pycache__", "utils.cpython-38.pyc")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, ".git", "config")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "venv", "lib", "python3.8", "site-packages")))

    def test_matching_wildcard_patterns(self):
        with open(os.path.join(self.test_dir, ".gitignore"), "w") as f:
            f.write("*.log\ntemp*\n")
        matcher = GitignoreMatcher(self.test_dir)
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "error.log")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "sub", "output.log")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "temp_data.csv")))
        self.assertFalse(matcher.is_ignored(os.path.join(self.test_dir, "item_temp.txt")))

    def test_absolute_vs_relative_gitignore_paths(self):
        with open(os.path.join(self.test_dir, ".gitignore"), "w") as f:
            f.write("/root_only.txt\nsub/ignored.txt\n")
        matcher = GitignoreMatcher(self.test_dir)
        
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "root_only.txt")))
        self.assertFalse(matcher.is_ignored(os.path.join(self.test_dir, "nested", "root_only.txt")))
        
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "sub", "ignored.txt")))
