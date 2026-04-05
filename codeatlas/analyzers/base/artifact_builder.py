"""Abstract base class for artifact builders."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from codeatlas.models.artifact_models import Artifact, DependencyRecord


class BaseArtifactBuilder(ABC):
    """Abstract base for builders that assemble final Artifact objects."""

    @abstractmethod
    def build(
        self,
        file_path: Path,
        raw_structure: dict[str, Any],
        dependencies: list[DependencyRecord],
    ) -> Artifact:
        """Build and return a complete Artifact from extracted data."""
        ...
