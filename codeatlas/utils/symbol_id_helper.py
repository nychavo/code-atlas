"""Symbol and dependency ID generation."""

from codeatlas.utils.hash_helper import HashHelper


class SymbolIdHelper:
    """Static utility methods for generating stable symbol identifiers."""

    @staticmethod
    def generate(artifact_id: str, symbol_name: str, kind: str) -> str:
        """Generate a stable symbol ID.

        The ID has the form ``symbol:<short_hash>`` where the hash is
        derived from the artifact ID, symbol name, and kind.
        """
        key = f"{artifact_id}:{symbol_name}:{kind}"
        return f"symbol:{HashHelper.short_hash(key, length=12)}"

    @staticmethod
    def generate_dependency_id(source: str, target: str, kind: str) -> str:
        """Generate a stable dependency ID.

        The ID has the form ``dep:<short_hash>`` where the hash is derived
        from the source, target, and kind.
        """
        key = f"{source}:{target}:{kind}"
        return f"dep:{HashHelper.short_hash(key, length=12)}"
