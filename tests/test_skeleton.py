import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from ai_pack import SkeletonExtractor

class TestSkeletonExtractor(unittest.TestCase):
    @patch('ai_pack.sys.stderr', new_callable=StringIO)
    def test_get_skeleton_success(self, mock_stderr):
        # Mock codesigs module in sys.modules
        mock_codesigs = MagicMock()
        mock_codesigs.file_sigs.return_value = ["def foo():", "    ..."]
        
        with patch.dict(sys.modules, {'codesigs': mock_codesigs}):
            result = SkeletonExtractor.get_skeleton("test.py", "def foo():\n    pass")
            self.assertEqual(result, "def foo():\n    ...")
            mock_codesigs.file_sigs.assert_called_once_with("test.py")

    @patch('ai_pack.sys.stderr', new_callable=StringIO)
    def test_get_skeleton_import_error(self, mock_stderr):
        with patch.dict(sys.modules, {'codesigs': None}):
            # Clear sys.modules of any real codesigs import to trigger ImportError
            original_modules = sys.modules.copy()
            if 'codesigs' in sys.modules:
                del sys.modules['codesigs']
            try:
                result = SkeletonExtractor.get_skeleton("test.py", "def foo():\n    pass")
                self.assertEqual(result, "def foo():\n    pass")
                self.assertIn("package is required", mock_stderr.getvalue())
            finally:
                sys.modules = original_modules

    @patch('ai_pack.sys.stderr', new_callable=StringIO)
    def test_get_skeleton_runtime_error(self, mock_stderr):
        mock_codesigs = MagicMock()
        mock_codesigs.file_sigs.side_effect = Exception("ast-grep not found")
        
        with patch.dict(sys.modules, {'codesigs': mock_codesigs}):
            result = SkeletonExtractor.get_skeleton("test.py", "def foo():\n    pass")
            self.assertEqual(result, "def foo():\n    pass")
            self.assertIn("codesigs failed", mock_stderr.getvalue())
