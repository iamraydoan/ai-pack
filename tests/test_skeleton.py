import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ai_pack.skeleton import SkeletonExtractor


class TestSkeletonExtractor(unittest.TestCase):
    def test_get_skeleton_python(self):
        code = "def foo(a: int) -> str:\n    print('hello')\n    return 'world'"
        result = SkeletonExtractor.get_skeleton("test.py", code)
        self.assertIn("def foo(a: int) -> str:\n     ...", result)
        self.assertNotIn("print('hello')", result)

    def test_get_skeleton_javascript(self):
        code = "function add(a, b) {\n    return a + b;\n}"
        result = SkeletonExtractor.get_skeleton("app.js", code)
        self.assertIn("function add(a, b) { ... }", result)
        self.assertNotIn("return a + b", result)

    def test_get_skeleton_unsupported_extension(self):
        code = "Random plain text content"
        result = SkeletonExtractor.get_skeleton("notes.txt", code)
        self.assertEqual(result, code)

    @patch("ai_pack.skeleton.sys.stderr", new_callable=StringIO)
    def test_get_skeleton_import_error(self, mock_stderr):
        original_modules = sys.modules.copy()
        if "tree_sitter_languages" in sys.modules:
            del sys.modules["tree_sitter_languages"]
        try:
            with patch.dict(sys.modules, {"tree_sitter_languages": None}):
                result = SkeletonExtractor.get_skeleton("test.py", "def foo():\n    pass")
                self.assertEqual(result, "def foo():\n    pass")
                self.assertIn("package is required", mock_stderr.getvalue())
        finally:
            sys.modules = original_modules

    @patch("ai_pack.skeleton.sys.stderr", new_callable=StringIO)
    def test_get_skeleton_runtime_error(self, mock_stderr):
        with patch("tree_sitter_languages.get_parser", side_effect=Exception("Parser crashed")):
            result = SkeletonExtractor.get_skeleton("test.py", "def foo():\n    pass")
            self.assertEqual(result, "def foo():\n    pass")
            self.assertIn("tree-sitter extraction failed", mock_stderr.getvalue())
