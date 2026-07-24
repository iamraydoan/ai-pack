import os
import sys

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".cs": "c_sharp",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".sh": "bash",
    ".bash": "bash",
}

FUNCTION_NODE_TYPES = {
    "function_definition",
    "function_declaration",
    "method_definition",
    "method_declaration",
    "function_item",
    "arrow_function",
}


def is_binary(file_path: str) -> bool:
    """Checks if a file is binary by looking for null bytes in the first 1024 bytes."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except Exception:
        return True


class SkeletonExtractor:
    """Extracts structural outline (signatures, classes, imports) of code files using tree-sitter."""

    @staticmethod
    def get_skeleton(file_path: str, content: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        lang_name = LANGUAGE_MAP.get(ext)
        if not lang_name:
            return content

        try:
            from tree_sitter_languages import get_parser

            parser = get_parser(lang_name)
            code_bytes = content.encode("utf-8")
            tree = parser.parse(code_bytes)

            repl_text = b" ..." if lang_name == "python" else b"{ ... }"
            replacements = []

            def walk(node):
                if node.type in FUNCTION_NODE_TYPES:
                    body = node.child_by_field_name("body")
                    if body:
                        replacements.append((body.start_byte, body.end_byte, repl_text))
                for child in node.children:
                    walk(child)

            walk(tree.root_node)

            if not replacements:
                return content

            res = bytearray(code_bytes)
            for start, end, rtext in sorted(replacements, key=lambda x: x[0], reverse=True):
                res[start:end] = rtext

            return res.decode("utf-8", errors="replace")
        except ImportError:
            print(
                "⚠️ Error: 'tree-sitter' or 'tree-sitter-languages' package is required for --skeleton mode.",
                file=sys.stderr,
            )
            print("💡 Please install dependencies using: pip install ai-pack-cli", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ tree-sitter extraction failed for {file_path}: {e}", file=sys.stderr)

        return content
