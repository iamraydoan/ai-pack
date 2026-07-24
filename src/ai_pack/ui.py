import os
import sys
from typing import List


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
            "Select files to pack (Space to toggle, Enter to confirm):", choices=choices
        ).ask()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Cancelled by user.")
        sys.exit(0)

    if selected is None:
        print("\n👋 Cancelled by user.")
        sys.exit(0)

    return selected
