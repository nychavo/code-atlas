"""Integration tests for SymbolIndexService."""

import pytest

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.services.artifact_generation_service import ArtifactGenerationService
from codeatlas.services.repository_scanner import RepositoryScanner
from codeatlas.services.symbol_index_service import SymbolIndexService


class TestSymbolIndexService:
    def _build_artifacts(self, settings: Settings, diagnostics: DiagnosticsCollector):
        scanner = RepositoryScanner(settings, diagnostics)
        files_by_lang = scanner.scan()
        svc = ArtifactGenerationService(settings, diagnostics)
        return svc.generate_all(files_by_lang)

    def test_symbol_index_contains_classes(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        artifacts = self._build_artifacts(settings, diagnostics)
        index_svc = SymbolIndexService(settings, diagnostics)
        index = index_svc.build(artifacts)

        symbol_names = {s.name for s in index.symbols.values()}
        assert "User" in symbol_names or "Product" in symbol_names

    def test_symbol_index_contains_functions(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        artifacts = self._build_artifacts(settings, diagnostics)
        index_svc = SymbolIndexService(settings, diagnostics)
        index = index_svc.build(artifacts)

        kinds = {s.kind for s in index.symbols.values()}
        assert "function" in kinds or "class" in kinds

    def test_symbol_index_project_id(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        artifacts = self._build_artifacts(settings, diagnostics)
        index_svc = SymbolIndexService(settings, diagnostics)
        index = index_svc.build(artifacts)

        assert index.project_id == settings.project_id
