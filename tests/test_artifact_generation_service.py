"""Integration tests for ArtifactGenerationService."""

from pathlib import Path

import pytest

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.services.artifact_generation_service import ArtifactGenerationService
from codeatlas.services.repository_scanner import RepositoryScanner


class TestArtifactGenerationService:
    def test_generates_artifacts_for_sample_project(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        scanner = RepositoryScanner(settings, diagnostics)
        files_by_lang = scanner.scan()

        service = ArtifactGenerationService(settings, diagnostics)
        artifacts = service.generate_all(files_by_lang)

        assert len(artifacts) > 0

    def test_artifact_has_correct_project_id(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        scanner = RepositoryScanner(settings, diagnostics)
        files_by_lang = scanner.scan()
        service = ArtifactGenerationService(settings, diagnostics)
        artifacts = service.generate_all(files_by_lang)

        for artifact in artifacts:
            assert artifact.project_id == settings.project_id

    def test_artifact_json_is_written(
        self, settings: Settings, diagnostics: DiagnosticsCollector, tmp_output_dir: Path
    ) -> None:
        scanner = RepositoryScanner(settings, diagnostics)
        files_by_lang = scanner.scan()
        service = ArtifactGenerationService(settings, diagnostics)
        artifacts = service.generate_all(files_by_lang)

        artifact_dir = tmp_output_dir / "artifacts"
        written = list(artifact_dir.glob("*.json"))
        assert len(written) == len(artifacts)

    def test_artifact_contains_classes_from_models(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        scanner = RepositoryScanner(settings, diagnostics)
        files_by_lang = scanner.scan()
        service = ArtifactGenerationService(settings, diagnostics)
        artifacts = service.generate_all(files_by_lang)

        models_artifact = next(
            (a for a in artifacts if "models" in a.module_name), None
        )
        assert models_artifact is not None
        class_names = {c.name for c in models_artifact.classes}
        assert "User" in class_names or "Product" in class_names
