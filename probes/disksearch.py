"""Finds files that contain a secret, as UTF-8 or UTF-16LE bytes."""
import os

MAX_BYTES = 50 * 1024 * 1024


def find_secret(root: str, secret: str) -> list:
    needles = [secret.encode("utf-8"), secret.encode("utf-16le")]
    hits = []
    for folder, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(folder, name)
            try:
                if os.path.getsize(path) > MAX_BYTES:
                    continue
                with open(path, "rb") as f:
                    data = f.read()
            except OSError:
                continue
            if any(needle in data for needle in needles):
                hits.append(os.path.relpath(path, root))
    return sorted(hits)
