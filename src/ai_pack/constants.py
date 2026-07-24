"""Extension mappings and predefined prompts for ai-pack."""

# Extension map for markdown syntax highlighting
EXTENSION_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "jsx",
    ".tsx": "tsx",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".md": "markdown",
    ".sh": "bash",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".rs": "rust",
    ".go": "go",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".cs": "csharp",
    ".xml": "xml",
    ".ini": "ini",
    ".toml": "toml",
    ".sql": "sql",
}

# Pre-defined system prompts
PROMPTS = {
    "review": "You are an expert Senior Developer. Please review the following codebase for code quality, architectural improvements, and best practices.",
    "bug": "You are a Security Engineer. Please analyze the following codebase to find potential bugs, edge cases, and security vulnerabilities.",
    "explain": "Please explain the architecture and workflow of the following codebase in a clear, easy-to-understand manner.",
}
