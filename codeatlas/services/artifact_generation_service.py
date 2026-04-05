"""Artifact generation service — coordinates analysis of all discovered files."""

import logging
from pathlib import Path

from codeatlas.analyzers.factory import AnalyzerFactory
from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.models.artifact_models import Artifact
from codeatlas.services.json_serialization_service import JsonSerializationService


class ArtifactGenerationService:
    """Generates and persists Artifact objects for all discovered source files."""

    def __init__(self, settings: Settings, diagnostics: DiagnosticsCollector) -> None:
        self.settings = settings
        self.diagnostics = diagnostics
        self.factory = AnalyzerFactory(settings, diagnostics)
        self.json_service = JsonSerializationService(settings)
        self.logger = logging.getLogger(__name__)

    def generate_all(self, files_by_language: dict[str, list[Path]]) -> list[Artifact]:
        """Analyse all files in *files_by_language* and return generated artifacts."""
        artifacts: list[Artifact] = []
        for lang, files in files_by_language.items():
            for file_path in files:
                try:
                    artifact = self.factory.analyze_file(file_path, lang)
                    if artifact:
                        self.json_service.write_artifact(artifact)
                        artifacts.append(artifact)
                        self.logger.debug("Generated artifact for %s", file_path)
                except Exception as exc:  # noqa: BLE001
                    self.diagnostics.add_error(
                        f"Failed to generate artifact for {file_path}: {exc}",
                        file_path=str(file_path),
                    )
        self.logger.info("Generated %d artifacts", len(artifacts))
        return artifacts
