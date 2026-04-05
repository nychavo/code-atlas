"""Integration tests for DependencyGraphService."""

import pytest

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.services.artifact_generation_service import ArtifactGenerationService
from codeatlas.services.dependency_graph_service import DependencyGraphService
from codeatlas.services.repository_scanner import RepositoryScanner


class TestDependencyGraphService:
    def _build_artifacts(self, settings: Settings, diagnostics: DiagnosticsCollector):
        scanner = RepositoryScanner(settings, diagnostics)
        files_by_lang = scanner.scan()
        service = ArtifactGenerationService(settings, diagnostics)
        return service.generate_all(files_by_lang)

    def test_graph_contains_all_artifacts(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        artifacts = self._build_artifacts(settings, diagnostics)
        graph_service = DependencyGraphService(settings, diagnostics)
        graph = graph_service.build(artifacts)

        assert set(graph.artifacts) == {a.artifact_id for a in artifacts}

    def test_graph_has_dependency_edges(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        artifacts = self._build_artifacts(settings, diagnostics)
        graph_service = DependencyGraphService(settings, diagnostics)
        graph = graph_service.build(artifacts)

        assert len(graph.dependency_edges) > 0

    def test_graph_schema_version(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        artifacts = self._build_artifacts(settings, diagnostics)
        graph_service = DependencyGraphService(settings, diagnostics)
        graph = graph_service.build(artifacts)

        assert graph.schema_version == settings.schema_version
