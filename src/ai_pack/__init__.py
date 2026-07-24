"""ai-pack: Pack your codebase into a single formatted Markdown string for LLMs."""

__version__ = "0.2.0"

from .cli import main
from .git import GitHelper, GitignoreMatcher
from .packer import get_candidate_files, pack_files, walk_dir
from .skeleton import SkeletonExtractor, is_binary

__all__ = [
    "is_binary",
    "SkeletonExtractor",
    "GitHelper",
    "GitignoreMatcher",
    "pack_files",
    "get_candidate_files",
    "walk_dir",
    "main",
]
