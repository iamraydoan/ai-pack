import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ai_pack import __version__
from ai_pack.cli import parse_args


class TestCli(unittest.TestCase):
    def test_version_flag(self):
        with patch.object(sys, "argv", ["ai-pack", "-v"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    parse_args()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn(__version__, mock_stdout.getvalue())

    def test_version_long_flag(self):
        with patch.object(sys, "argv", ["ai-pack", "--version"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    parse_args()
                self.assertEqual(cm.exception.code, 0)
                self.assertIn(__version__, mock_stdout.getvalue())
