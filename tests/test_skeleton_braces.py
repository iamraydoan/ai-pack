import unittest
from ai_pack import SkeletonExtractor

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

    def test_typescript_return_types(self):
        ts_code = """class Manager {
    async getItems(req: Request): Promise<Item[]> {
        return this.client.get();
    }
    
    add(a: number, b: number): number {
        return a + b;
    }
}
"""
        expected = """class Manager {
    async getItems(req: Request): Promise<Item[]>  { /* ... */ }
    
    add(a: number, b: number): number  { /* ... */ }
}"""
        self.assertEqual(SkeletonExtractor.extract_brace_skeleton(ts_code).strip(), expected.strip())
