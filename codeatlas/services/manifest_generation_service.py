"""Manifest generation service — produces a project manifest from artifacts."""

import logging
from datetime import datetime, timezone
from pathlib import Path

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.models.artifact_models import Artifact
from codeatlas.models.manifest_models import ArtifactEntry, Manifest
from codeatlas.utils.path_helper import PathHelper


class ManifestGenerationService:
    """Generates a Manifest describing all analysis output for a project."""

    def __init__(self, settings: Settings, diagnostics: DiagnosticsCollector) -> None:
        self.settings = settings
        self.diagnostics = diagnostics
        self.logger = logging.getLogger(__name__)

    def build(self, artifacts: list[Artifact]) -> Manifest:
        """Build and return a :class:`~codeatlas.models.manifest_models.Manifest`."""
        output_dir = self.settings.output_dir
        artifact_dir = output_dir / "artifacts"

        entries: list[ArtifactEntry] = []
        languages: set[str] = set()
        for artifact in artifacts:
            filename = PathHelper.get_artifact_filename(artifact.artifact_id)
            entries.append(
                ArtifactEntry(
                    artifact_id=artifact.artifact_id,
                    path=artifact.relative_path,
                    module_name=artifact.module_name,
                    language=artifact.language,
                    artifact_file=str(artifact_dir / filename),
                )
            )
            languages.add(artifact.language)

        return Manifest(
            schema_version=self.settings.schema_version,
            project_id=self.settings.project_id,
            project_name=self.settings.project_name,
            root_path=str(self.settings.root_path),
            artifact_directory=str(artifact_dir),
            graph_file=str(output_dir / "master_dependency_graph.json"),
            symbol_index_file=str(output_dir / "symbol_index.json"),
            manifest_file=str(output_dir / "manifest.json"),
            entry_points=[],
            artifacts=entries,
            total_files=len(artifacts),
            total_artifacts=len(artifacts),
            languages=sorted(languages),
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={"analyzer_version": "0.1.0"},
        )
