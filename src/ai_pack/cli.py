import argparse
import os
import sys

from .constants import PROMPTS
from .packer import get_candidate_files, pack_files
from .ui import interactive_select
from .utils import copy_via_osc52


def parse_args():
    parser = argparse.ArgumentParser(
        description="📦 ai-pack: Pack your codebase into a single formatted Markdown string for LLMs."
    )
    parser.add_argument(
        "-f", "--files", nargs="+", help="Explicitly specify files or directories to pack, ignoring the rest."
    )
    parser.add_argument(
        "-c", "--changed", action="store_true", help="Only pack uncommitted or modified files (requires Git)."
    )
    parser.add_argument(
        "-s",
        "--skeleton",
        action="store_true",
        help="Extract only class definitions, function signatures, and imports/exports to save tokens.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Display an interactive checkbox list in the terminal to select files to pack.",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        choices=["review", "bug", "explain"],
        help="Prepend a pre-defined system prompt to the beginning of the output.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Save the final Markdown output to the specified file path instead of copying to clipboard.",
    )
    parser.add_argument(
        "--max-tokens", type=int, help="Count approximate tokens. Warning if payload exceeds this limit."
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
            print(
                f"⚠️ Warning: The payload is approximately {approx_tokens:,} tokens, which exceeds your limit of {args.max_tokens:,} tokens."
            )
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
            print(
                "💡 In headless Linux systems, you must install 'xclip' or 'xsel', or direct output to a file using the '-o' flag.",
                file=sys.stderr,
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
