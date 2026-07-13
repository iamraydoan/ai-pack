import unittest
from ai_pack import SkeletonExtractor

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

    def test_single_line_and_comments(self):
        code = """def simple_get(self): return self.x

def comment_sig(a, b): # basic add
    return a + b
"""
        expected = """def simple_get(self): return self.x
def comment_sig(a, b): # basic add
    ..."""
        self.assertEqual(SkeletonExtractor.extract_python_skeleton(code).strip(), expected.strip())
