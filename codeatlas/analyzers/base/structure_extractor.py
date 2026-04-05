"""Abstract base class for structure extractors."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseStructureExtractor(ABC):
    """Abstract base for extractors that parse source files into raw dicts."""

    @abstractmethod
    def extract(self, file_path: Path, source_code: str) -> dict[str, Any]:
        """Extract structural information from *source_code*.

        Returns a raw dictionary suitable for passing to a SymbolResolver
        or ArtifactBuilder.
        """
        ...
