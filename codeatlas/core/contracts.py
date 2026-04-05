"""Protocol definitions for CodeAtlas analyzer components."""

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from codeatlas.models.artifact_models import Artifact, DependencyRecord, SummaryRecord


@runtime_checkable
class LanguageAnalyzerProtocol(Protocol):
    """Protocol for language-specific analyzers."""

    def analyze(self, file_path: Path) -> Artifact | None:
        """Analyze a source file and return an Artifact, or None on failure."""
        ...


@runtime_checkable
class StructureExtractorProtocol(Protocol):
    """Protocol for structure extractors."""

    def extract(self, file_path: Path, source_code: str) -> dict[str, Any]:
        """Extract structural information from source code."""
        ...


@runtime_checkable
class SymbolResolverProtocol(Protocol):
    """Protocol for symbol resolvers."""

    def resolve(self, file_path: Path, raw_structure: dict[str, Any]) -> dict[str, Any]:
        """Resolve symbols and enrich raw structure data."""
        ...


@runtime_checkable
class DependencyExtractorProtocol(Protocol):
    """Protocol for dependency extractors."""

    def extract_dependencies(self, file_path: Path, raw_structure: dict[str, Any]) -> list[DependencyRecord]:
        """Extract dependency records from resolved structure."""
        ...


@runtime_checkable
class ArtifactBuilderProtocol(Protocol):
    """Protocol for artifact builders."""

    def build(self, file_path: Path, raw_structure: dict[str, Any], dependencies: list[DependencyRecord]) -> Artifact:
        """Build a complete Artifact from extracted data."""
        ...


@runtime_checkable
class SummaryGeneratorProtocol(Protocol):
    """Protocol for summary generators."""

    def generate_summary(self, artifact_data: dict[str, Any], settings: Any) -> SummaryRecord:
        """Generate a SummaryRecord from artifact data."""
        ...
