"""Stable artifact ID generation."""

from codeatlas.utils.hash_helper import HashHelper


class ArtifactIdHelper:
    """Static utility methods for generating stable artifact identifiers."""

    @staticmethod
    def generate(project_id: str, relative_path: str) -> str:
        """Generate a stable artifact ID from *project_id* and *relative_path*.

        The returned ID has the form ``artifact:<project_id>:<short_hash>``
        where the hash is derived from the combined key.
        """
        key = f"{project_id}:{relative_path}"
        short = HashHelper.short_hash(key, length=12)
        return f"artifact:{project_id}:{short}"
