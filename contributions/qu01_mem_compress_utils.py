import base64
import zlib


def compress_text(text: str) -> str:
    """Compress UTF-8 text to a base64‑encoded zlib payload.

    Returns a string that can be safely stored in a context fragment.
    """
    compressed = zlib.compress(text.encode("utf-8"))
    return base64.b64encode(compressed).decode("ascii")


def decompress_text(payload: str) -> str:
    """Decompress a base64‑encoded zlib payload back to UTF‑8 text.

    Raises a ValueError if the payload is not valid.
    """
    try:
        raw = base64.b64decode(payload.encode("ascii"))
        return zlib.decompress(raw).decode("utf-8")
    except Exception as e:
        raise ValueError("Invalid compressed payload") from e

# Simple self‑test
if __name__ == "__main__":
    sample = "The quick brown fox jumps over the lazy dog."
    comp = compress_text(sample)
    print("Compressed:", comp)
    print("Decompressed:", decompress_text(comp))
