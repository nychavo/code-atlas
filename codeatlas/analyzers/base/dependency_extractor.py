"""Abstract base class for dependency extractors."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from codeatlas.models.artifact_models import DependencyRecord


class BaseDependencyExtractor(ABC):
    """Abstract base for extractors that produce dependency records."""

    @abstractmethod
    def extract_dependencies(self, file_path: Path, raw_structure: dict[str, Any]) -> list[DependencyRecord]:
        """Return dependency records derived from *raw_structure*."""
        ...
