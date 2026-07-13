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
        # Non-existent files should return True (ignored) instead of crashing
        self.assertTrue(is_binary(os.path.join(self.test_dir, "does_not_exist.bin")))


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
        
        # Starts with /: matches only at root
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "root_only.txt")))
        self.assertFalse(matcher.is_ignored(os.path.join(self.test_dir, "nested", "root_only.txt")))
        
        # Relative path matches nested folder structure
        self.assertTrue(matcher.is_ignored(os.path.join(self.test_dir, "sub", "ignored.txt")))


class TestPythonSkeletonExtractor(unittest.TestCase):
    def test_basic_functions_and_classes(self):
        code = """class User:
    def __init__(self, name):
        self.name = name
    def greet(self):
        print("Hello " + self.name)
"""
        expected = """class User:
    def __init__(self, name):
        ...
    def greet(self):
        ..."""
        self.assertEqual(SkeletonExtractor.extract_python_skeleton(code).strip(), expected.strip())

    def test_decorators_and_async(self):
        code = """@property
@cache
def value(self):
    return self._val

async def fetch_data(url):
    res = await client.get(url)
    return res.json()
"""
        expected = """@property
@cache
def value(self):
    ...
async def fetch_data(url):
    ..."""
        self.assertEqual(SkeletonExtractor.extract_python_skeleton(code).strip(), expected.strip())

    def test_multiline_signatures(self):
        code = """def complex_function(
    a: int,
    b: str,
    c: float = 1.0
) -> bool:
    print(a, b, c)
    return True
"""
        expected = """def complex_function(
    a: int,
    b: str,
    c: float = 1.0
) -> bool:
    ..."""
        self.assertEqual(SkeletonExtractor.extract_python_skeleton(code).strip(), expected.strip())


class TestBraceSkeletonExtractor(unittest.TestCase):
    def test_javascript_typescript(self):
        js_code = """import { component } from 'framework';
const PORT = 8080;

export default class Widget extends Base {
    constructor(config) {
        super(config);
        this.init();
    }

    render() {
        return `<div>${this.config.title}</div>`;
    }
}

const add = (a, b) => {
    return a + b;
};
"""
        expected = """import { component } from 'framework';
const PORT = 8080;

export default class Widget extends Base {
    constructor(config)  { /* ... */ }

    render()  { /* ... */ }
}

const add = (a, b) =>  { /* ... */ };"""
        self.assertEqual(SkeletonExtractor.extract_brace_skeleton(js_code).strip(), expected.strip())

    def test_js_template_literals_with_braces(self):
        # Make sure that `${val}` inside template strings does not break brace matching
        js_code = """const render = (name) => {
    return `Hello, ${name}! Your age is ${getAge({birth: 1990})}.`;
};
"""
        expected = """const render = (name) =>  { /* ... */ };"""
        self.assertEqual(SkeletonExtractor.extract_brace_skeleton(js_code).strip(), expected.strip())

    def test_golang_parser(self):
        go_code = """package main
import "fmt"

type Server struct {
    Port int
}

func NewServer(port int) *Server {
    return &Server{Port: port}
}

func (s *Server) Start() error {
    fmt.Println("Starting...")
    return nil
}
"""
        expected = """package main
import "fmt"

type Server struct {
    Port int
}

func NewServer(port int) *Server  { /* ... */ }

func (s *Server) Start() error  { /* ... */ }"""
        self.assertEqual(SkeletonExtractor.extract_brace_skeleton(go_code).strip(), expected.strip())

    def test_rust_parser(self):
        rust_code = """use std::io;

pub struct Robot {
    name: String,
}

impl Robot {
    pub fn new(name: &str) -> Self {
        Robot {
            name: name.to_string(),
        }
    }

    fn speak(&self) {
        println!("Hello, my name is {}", self.name);
    }
}
"""
        expected = """use std::io;

pub struct Robot {
    name: String,
}

impl Robot {
    pub fn new(name: &str) -> Self  { /* ... */ }

    fn speak(&self)  { /* ... */ }
}"""
        self.assertEqual(SkeletonExtractor.extract_brace_skeleton(rust_code).strip(), expected.strip())

    def test_cpp_java_parser(self):
        java_code = """public class App {
    public static void main(String[] args) {
        System.out.println("Hello World!");
    }
    
    private int calc(int a) {
        return a * 2;
    }
}
"""
        expected = """public class App {
    public static void main(String[] args)  { /* ... */ }
    
    private int calc(int a)  { /* ... */ }
}"""
        self.assertEqual(SkeletonExtractor.extract_brace_skeleton(java_code).strip(), expected.strip())


if __name__ == "__main__":
    unittest.main()
