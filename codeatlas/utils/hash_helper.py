"""Cryptographic hash helpers."""

import hashlib
from pathlib import Path


class HashHelper:
    """Static utility methods for hashing files and strings."""

    @staticmethod
    def hash_file(path: Path) -> str:
        """Return the SHA-256 hex digest of the file at *path*."""
        digest = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def hash_string(s: str) -> str:
        """Return the SHA-256 hex digest of *s* encoded as UTF-8."""
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    @staticmethod
    def short_hash(s: str, length: int = 8) -> str:
        """Return the first *length* characters of the SHA-256 hex digest of *s*."""
        return HashHelper.hash_string(s)[:length]
