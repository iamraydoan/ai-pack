import sys


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
