import os
import sys
from typing import List, Set

from .constants import EXTENSION_MAP
from .git import GitHelper, GitignoreMatcher
from .skeleton import SkeletonExtractor, is_binary


def walk_dir(directory: str, git_files: Set[str] = None, gitignore: GitignoreMatcher = None) -> List[str]:
    """Recursively traverses directories, ignoring binaries and configured ignore directories."""
    candidates = []
    for root, dirs, files in os.walk(directory):
        # Exclude common large/temporary directories in-place
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ("node_modules", "__pycache__", "venv", "env", "dist", "build", "target")
        ]

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
