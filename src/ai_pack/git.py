import fnmatch
import os
import subprocess
import sys
from typing import Set


class GitHelper:
    """Helper class to interact with Git shell commands."""

    @staticmethod
    def is_git_repo(path: str) -> bool:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return res.returncode == 0 and res.stdout.strip() == "true"
        except Exception:
            return False

    @staticmethod
    def get_git_root(path: str) -> str:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
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
                cwd=path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
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
                ["git", "diff", "--name-only"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if res_diff.returncode == 0:
                for line in res_diff.stdout.splitlines():
                    if line.strip():
                        changed.add(os.path.abspath(os.path.join(git_root, line.strip())))

            # 2. Staged files
            res_diff_cached = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if res_diff_cached.returncode == 0:
                for line in res_diff_cached.stdout.splitlines():
                    if line.strip():
                        changed.add(os.path.abspath(os.path.join(git_root, line.strip())))

            # 3. Untracked files
            res_status = subprocess.run(
                ["git", "status", "--porcelain"], cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
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
                if (
                    fnmatch.fnmatch(rel_path, f"**/{pat}")
                    or fnmatch.fnmatch(rel_path, pat)
                    or any(fnmatch.fnmatch(part, pat) for part in parts)
                ):
                    return True

        return False
