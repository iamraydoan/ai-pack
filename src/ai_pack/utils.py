import base64
import sys


def copy_via_osc52(payload: str) -> bool:
    """Attempts to copy text to the client system clipboard using OSC 52 escape sequence."""
    try:
        # Base64 encode the payload
        b64_data = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        # Write to stdout using the OSC 52 escape sequence: \x1b]52;c;[base64]\x07
        sys.stdout.write(f"\x1b]52;c;{b64_data}\x07")
        sys.stdout.flush()
        return True
    except Exception:
        return False
