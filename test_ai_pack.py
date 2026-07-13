import unittest
import os
import tempfile
import shutil
from ai_pack import is_binary, GitignoreMatcher, SkeletonExtractor


class TestBinaryDetection(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_text_file(self):
        file_path = os.path.join(self.test_dir, "text.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Hello, this is a plain text file.")
        self.assertFalse(is_binary(file_path))

    def test_binary_file(self):
        file_path = os.path.join(self.test_dir, "binary.bin")
        with open(file_path, "wb") as f:
            f.write(b"Hello\x00world binary content")
        self.assertTrue(is_binary(file_path))


class TestGitignoreMatcher(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_default_ignores(self):
        matcher = GitignoreMatcher(self.test_dir)
        
        # node_modules and pycache should be ignored by default
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "node_modules", "package.json")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "__pycache__", "main.pyc")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, ".venv", "bin", "python")))
        
        # Normal files should not be ignored
        self.assertFalse(matcher.is_ignored(os.path.join(self.test_dir, "src", "main.py")))

    def test_custom_gitignore_rules(self):
        # Create a mock .gitignore file
        gitignore_content = """
# Ignore all logs
*.log
# Ignore temp directory
/temp/
# Ignore secret files anywhere
secrets.json
"""
        with open(os.path.join(self.test_dir, ".gitignore"), "w", encoding="utf-8") as f:
            f.write(gitignore_content)
            
        matcher = GitignoreMatcher(self.test_dir)
        
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "app.log")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "logs", "error.log")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "temp", "anyfile.txt")))
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "config", "secrets.json")))
        
        # Files not matching rules should not be ignored
        self.assertFalse(matcher.is_ignored(os.path.join(self.test_dir, "src", "app.py")))
        self.assertFalse(matcher.is_ignored(os.path.join(self.test_dir, "templates", "index.html")))


class TestSkeletonExtractor(unittest.TestCase):
    def test_python_skeleton(self):
        python_code = """import os

@decorator
class MyClass:
    \"\"\"Docstring class.\"\"\"
    
    def __init__(self, val):
        self.val = val
        print(self.val)
        
    def get_val(self):
        return self.val

def top_level_func(a, b):
    # comment inside
    return a + b
"""
        expected_skeleton = """import os

@decorator
class MyClass:
    \"\"\"Docstring class.\"\"\"
    
    def __init__(self, val):
        ...
    def get_val(self):
        ...
def top_level_func(a, b):
    ..."""
        skeleton = SkeletonExtractor.extract_python_skeleton(python_code)
        self.assertEqual(skeleton.strip(), expected_skeleton.strip())

    def test_brace_skeleton(self):
        js_code = """import { helper } from './utils';

const x = 10;

export class Calculator {
    constructor(val) {
        this.val = val;
    }
    
    add(a, b) {
        if (a > 0) {
            return a + b;
        }
        return b;
    }
}

function compute(data) {
    return data.map(x => x * 2);
}
"""
        expected_skeleton = """import { helper } from './utils';

const x = 10;

export class Calculator {
    constructor(val)  { /* ... */ }
    
    add(a, b)  { /* ... */ }
}

function compute(data)  { /* ... */ }"""
        
        skeleton = SkeletonExtractor.extract_brace_skeleton(js_code)
        self.assertEqual(skeleton.strip(), expected_skeleton.strip())


if __name__ == "__main__":
    unittest.main()
