#!/usr/bin/env python3
import os
import sys
import re
import argparse
import subprocess
import fnmatch
from typing import List, Set

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
    "explain": "Please explain the architecture and workflow of the following codebase in a clear, easy-to-understand manner."
}


class GitHelper:
    """Helper class to interact with Git shell commands."""

    @staticmethod
    def is_git_repo(path: str) -> bool:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            return res.returncode == 0 and res.stdout.strip() == "true"
        except Exception:
            return False

    @staticmethod
    def get_git_root(path: str) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if res.returncode == 0:
                return os.path.abspath(res.stdout.strip())
        except Exception:
            pass
        return os.path.abspath(path)

    @staticmethod
    def get_all_non_ignored_files(path: str) -> Set[str]:
        """Returns all tracked and untracked but non-ignored files in the repository."""
        try:
            res = subprocess.run(
                ["git", "ls-files", "--full-name", "--cached", "--others", "--exclude-standard"],
                cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if res.returncode == 0:
                files = set()
                git_root = GitHelper.get_git_root(path)
                for line in res.stdout.splitlines():
                    if line.strip():
                        abs_path = os.path.abspath(os.path.join(git_root, line.strip()))
                        files.add(abs_path)
                return files
        except Exception as e:
            print(f"⚠️ Warning: Could not list git files: {e}", file=sys.stderr)
        return set()

    @staticmethod
    def get_changed_files(path: str) -> Set[str]:
        """Returns all modified, staged, and untracked files."""
        changed = set()
        git_root = GitHelper.get_git_root(path)
        try:
            # 1. Uncommitted and modified tracked files
            res_diff = subprocess.run(
                ["git", "diff", "--name-only"],
                cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if res_diff.returncode == 0:
                for line in res_diff.stdout.splitlines():
                    if line.strip():
                        changed.add(os.path.abspath(os.path.join(git_root, line.strip())))
            
            # 2. Staged files
            res_diff_cached = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if res_diff_cached.returncode == 0:
                for line in res_diff_cached.stdout.splitlines():
                    if line.strip():
                        changed.add(os.path.abspath(os.path.join(git_root, line.strip())))

            # 3. Untracked files
            res_status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if res_status.returncode == 0:
                for line in res_status.stdout.splitlines():
                    if line.startswith("?? "):
                        file_path = line[3:].strip()
                        changed.add(os.path.abspath(os.path.join(git_root, file_path)))
        except Exception as e:
            print(f"⚠️ Error querying Git changes: {e}", file=sys.stderr)
        return changed


class GitignoreMatcher:
    """Manual .gitignore matcher for non-git environments."""

    def __init__(self, base_dir: str):
        self.base_dir = os.path.abspath(base_dir)
        self.patterns = []
        
        gitignore_path = os.path.join(self.base_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            try:
                with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        self.patterns.append(line)
            except Exception:
                pass

    def is_ignored(self, file_path: str) -> bool:
        abs_path = os.path.abspath(file_path)
        rel_path = os.path.relpath(abs_path, self.base_dir)
        
        # Check standard default ignores
        parts = rel_path.split(os.sep)
        for part in parts:
            if part.startswith(".") and part != ".":
                return True
            if part in ("node_modules", "__pycache__", "venv", "env", "dist", "build", "target"):
                return True
                
        # Check patterns from .gitignore
        for pattern in self.patterns:
            pat = pattern
            is_dir_only = pat.endswith("/")
            if is_dir_only:
                pat = pat[:-1]
                
            if pat.startswith("/"):
                pat = pat[1:]
                if fnmatch.fnmatch(rel_path, pat) or fnmatch.fnmatch(os.path.dirname(rel_path), pat):
                    return True
            else:
                if fnmatch.fnmatch(rel_path, f"**/{pat}") or fnmatch.fnmatch(rel_path, pat) or any(fnmatch.fnmatch(part, pat) for part in parts):
                    return True
                    
        return False


def is_binary(file_path: str) -> bool:
    """Checks if a file is binary by looking for null bytes in the first 1024 bytes."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\x00" in chunk
    except Exception:
        return True


class SkeletonExtractor:
    """Extracts structural outline (signatures, classes, imports) of code files."""

    @staticmethod
    def get_skeleton(file_path: str, content: str) -> str:
        try:
            from codesigs import file_sigs
            sigs = file_sigs(file_path)
            if sigs is not None:
                return "\n".join(sigs)
        except ImportError:
            print("⚠️ Error: 'codesigs' package is required for --skeleton mode.", file=sys.stderr)
            print("💡 Please install it using: pip install ai-pack-cli (requires Python >= 3.9)", file=sys.stderr)
        except Exception as e:
            print(f"⚠️ codesigs failed for {file_path}: {e}", file=sys.stderr)
        return content


def copy_via_osc52(payload: str) -> bool:
    """Attempts to copy text to the client system clipboard using OSC 52 escape sequence."""
    try:
        import base64
        # Base64 encode the payload
        b64_data = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        # Write to stdout using the OSC 52 escape sequence: \x1b]52;c;[base64]\x07
        sys.stdout.write(f"\x1b]52;c;{b64_data}\x07")
        sys.stdout.flush()
        return True
    except Exception:
        return False


def walk_dir(directory: str, git_files: Set[str] = None, gitignore: GitignoreMatcher = None) -> List[str]:
    """Recursively traverses directories, ignoring binaries and configured ignore directories."""
    candidates = []
    for root, dirs, files in os.walk(directory):
        # Exclude common large/temporary directories in-place
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in (
            "node_modules", "__pycache__", "venv", "env", "dist", "build", "target"
        )]
        
        for file in files:
            full_path = os.path.abspath(os.path.join(root, file))
            
            # Check manual gitignore helper if in a non-git repo
            if gitignore and gitignore.is_ignored(full_path):
                continue
            
            # Check git list if in a git repo
            if git_files is not None and full_path not in git_files:
                continue
                
            if file.startswith("."):
                continue
                
            if is_binary(full_path):
                continue
                
            candidates.append(full_path)
    return candidates


def get_candidate_files(args) -> List[str]:
    """Combines CLI arguments to determine final list of files to pack."""
    cwd = os.getcwd()
    
    is_git = GitHelper.is_git_repo(cwd)
    git_files = GitHelper.get_all_non_ignored_files(cwd) if is_git else None
    gitignore = GitignoreMatcher(cwd) if not is_git else None
    
    if args.changed:
        if not is_git:
            print("❌ Error: --changed requires a Git repository.", file=sys.stderr)
            sys.exit(1)
        candidates = list(GitHelper.get_changed_files(cwd))
    else:
        if args.files:
            candidates = []
            for path in args.files:
                abs_path = os.path.abspath(path)
                if os.path.isdir(abs_path):
                    candidates.extend(walk_dir(abs_path, git_files, gitignore))
                elif os.path.isfile(abs_path):
                    if not is_binary(abs_path):
                        candidates.append(abs_path)
                    else:
                        print(f"⚠️ Skipping binary file: {path}")
                else:
                    print(f"⚠️ Path not found: {path}", file=sys.stderr)
        else:
            candidates = walk_dir(cwd, git_files, gitignore)
            
    # Apply filtering for combined --changed and --files
    if args.changed and args.files:
        filtered = []
        for path in args.files:
            abs_path = os.path.abspath(path)
            for cand in candidates:
                if os.path.commonpath([abs_path, cand]) == abs_path:
                    filtered.append(cand)
        candidates = list(set(filtered))
        
    # Remove duplicates, directories, non-existent, and binary files
    final_candidates = []
    for cand in sorted(list(set(candidates))):
        if os.path.exists(cand) and not os.path.isdir(cand) and not is_binary(cand):
            final_candidates.append(cand)
            
    return final_candidates


def interactive_select(files: List[str]) -> List[str]:
    """Displays an interactive checkbox list using questionary."""
    try:
        import questionary
    except ImportError:
        print("❌ Error: 'questionary' package is required for interactive mode.", file=sys.stderr)
        print("💡 Install it by running: pip install -e .", file=sys.stderr)
        sys.exit(1)
        
    cwd = os.getcwd()
    choices = []
    for f in files:
        rel = os.path.relpath(f, cwd)
        choices.append(questionary.Choice(title=rel, value=f, checked=False))
        
    if not choices:
        print("⚠️ No files available to select.")
        return []
        
    try:
        selected = questionary.checkbox(
            "Select files to pack (Space to toggle, Enter to confirm):",
            choices=choices
        ).ask()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Cancelled by user.")
        sys.exit(0)
        
    if selected is None:
        print("\n👋 Cancelled by user.")
        sys.exit(0)
        
    return selected


def pack_files(files: List[str], skeleton_mode: bool) -> str:
    """Reads and formats files into a single Markdown payload."""
    cwd = os.getcwd()
    output_blocks = []
    
    for file_path in files:
        rel_path = os.path.relpath(file_path, cwd)
        ext = os.path.splitext(file_path)[1].lower()
        lang = EXTENSION_MAP.get(ext, ext.lstrip("."))
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                
            if skeleton_mode:
                content = SkeletonExtractor.get_skeleton(file_path, content)
                
            block = f"### FILE: {rel_path}\n```{lang}\n{content}\n```"
            output_blocks.append(block)
        except Exception as e:
            print(f"⚠️ Error reading file {rel_path}: {e}", file=sys.stderr)
            
    return "\n\n".join(output_blocks)


def parse_args():
    parser = argparse.ArgumentParser(
        description="📦 ai-pack: Pack your codebase into a single formatted Markdown string for LLMs."
    )
    parser.add_argument(
        "-f", "--files",
        nargs="+",
        help="Explicitly specify files or directories to pack, ignoring the rest."
    )
    parser.add_argument(
        "-c", "--changed",
        action="store_true",
        help="Only pack uncommitted or modified files (requires Git)."
    )
    parser.add_argument(
        "-s", "--skeleton",
        action="store_true",
        help="Extract only class definitions, function signatures, and imports/exports to save tokens."
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Display an interactive checkbox list in the terminal to select files to pack."
    )
    parser.add_argument(
        "-p", "--prompt",
        choices=["review", "bug", "explain"],
        help="Prepend a pre-defined system prompt to the beginning of the output."
    )
    parser.add_argument(
        "-o", "--output",
        help="Save the final Markdown output to the specified file path instead of copying to clipboard."
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        help="Count approximate tokens. Warning if payload exceeds this limit."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Pre-checks for dependencies
    # If no output path is set, we will eventually need pyperclip, warn early but don't crash
    if not args.output:
        try:
            import pyperclip
        except ImportError:
            print("⚠️ Note: 'pyperclip' is not installed. Output copy to clipboard will fail.", file=sys.stderr)
            print("💡 Install dependencies via: pip install -e .", file=sys.stderr)
            print("💡 Or output directly to a file using the -o flag.", file=sys.stderr)
            print("-" * 50, file=sys.stderr)
            
    # Gather candidate files
    candidates = get_candidate_files(args)
    
    if not candidates:
        print("🔍 No files found matching your criteria.")
        sys.exit(0)
        
    # Interactive selection
    if args.interactive:
        selected_files = interactive_select(candidates)
    else:
        selected_files = candidates
        
    if not selected_files:
        print("🔍 No files selected.")
        sys.exit(0)
        
    # Pack files
    print(f"📦 Packing {len(selected_files)} files...")
    payload = pack_files(selected_files, args.skeleton)
    
    # Prepend prompt if specified
    if args.prompt:
        prompt_text = PROMPTS[args.prompt]
        payload = f"{prompt_text}\n\n{payload}"
        
    # Calculate stats
    char_count = len(payload)
    word_count = len(payload.split())
    approx_tokens = char_count // 4  # Standard ~4 characters per token heuristic
    
    print(f"📊 Stats: {char_count:,} characters | {word_count:,} words | ~{approx_tokens:,} tokens")
    
    # Check max-tokens limit
    if args.max_tokens:
        if approx_tokens > args.max_tokens:
            print(f"⚠️ Warning: The payload is approximately {approx_tokens:,} tokens, which exceeds your limit of {args.max_tokens:,} tokens.")
            try:
                confirm = input("Do you want to proceed? (y/n): ").strip().lower()
                if confirm not in ("y", "yes"):
                    print("👋 Aborted.")
                    sys.exit(0)
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Aborted.")
                sys.exit(0)
                
    # Output operations
    if args.output:
        try:
            # Create directories if they don't exist
            out_dir = os.path.dirname(args.output)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(payload)
            print(f"🚀 Successfully saved to {args.output}!")
        except Exception as e:
            print(f"❌ Error saving to file {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        copied = False
        try:
            import pyperclip
            pyperclip.copy(payload)
            copied = True
            print("🚀 Successfully copied to clipboard!")
        except Exception:
            # Fallback to OSC 52 (works seamlessly over SSH / remote terminal sessions)
            if copy_via_osc52(payload):
                copied = True
                print("🚀 Successfully copied to clipboard (via OSC 52 remote sequence)!")
                
        if not copied:
            print("❌ Error copying to clipboard: Pyperclip could not find a copy/paste mechanism.", file=sys.stderr)
            print("💡 In headless Linux systems, you must install 'xclip' or 'xsel', or direct output to a file using the '-o' flag.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
