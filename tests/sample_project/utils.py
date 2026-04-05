"""Sample utility functions for the test project."""

import hashlib
import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

MAX_NAME_LENGTH: int = 100


def validate_email(email: str) -> bool:
    """Return True if *email* is a syntactically valid email address."""
    return bool(EMAIL_REGEX.match(email))


def truncate(text: str, max_length: int = MAX_NAME_LENGTH) -> str:
    """Truncate *text* to *max_length* characters, appending '…' if needed."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"


def hash_value(value: str) -> str:
    """Return a SHA-256 hex digest of *value* (demo utility — not for security-sensitive use)."""
    return hashlib.sha256(value.encode()).hexdigest()
