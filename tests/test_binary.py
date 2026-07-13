import unittest
import os
import tempfile
import shutil
from ai_pack import is_binary

class TestBinaryDetection(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_text_file_is_not_binary(self):
        file_path = os.path.join(self.test_dir, "text.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Hello, this is a plain text file with normal characters.")
        self.assertFalse(is_binary(file_path))

    def test_empty_file_is_not_binary(self):
        file_path = os.path.join(self.test_dir, "empty.txt")
        with open(file_path, "w") as f:
            f.write("")
        self.assertFalse(is_binary(file_path))

    def test_binary_file_with_null_byte_is_binary(self):
        file_path = os.path.join(self.test_dir, "binary.bin")
        with open(file_path, "wb") as f:
            f.write(b"PNG\x00\x00\x00\r\nIHDR")
        self.assertTrue(is_binary(file_path))

    def test_missing_file_is_treated_as_binary(self):
        self.assertTrue(is_binary(os.path.join(self.test_dir, "does_not_exist.bin")))
