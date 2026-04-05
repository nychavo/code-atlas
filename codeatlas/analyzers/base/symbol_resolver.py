"""Abstract base class for symbol resolvers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseSymbolResolver(ABC):
    """Abstract base for resolvers that enrich raw structure data."""

    @abstractmethod
    def resolve(self, file_path: Path, raw_structure: dict[str, Any]) -> dict[str, Any]:
        """Resolve symbols referenced in *raw_structure* and return an enriched copy."""
        ...
