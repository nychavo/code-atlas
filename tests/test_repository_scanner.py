"""Tests for RepositoryScanner."""

from pathlib import Path

import pytest

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.services.repository_scanner import RepositoryScanner


class TestRepositoryScanner:
    def test_scan_returns_python_files(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        scanner = RepositoryScanner(settings, diagnostics)
        result = scanner.scan()
        assert "python" in result
        assert len(result["python"]) > 0

    def test_scan_paths_are_absolute(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        scanner = RepositoryScanner(settings, diagnostics)
        result = scanner.scan()
        for files in result.values():
            for f in files:
                assert f.is_absolute()

    def test_scan_excludes_pycache(
        self, settings: Settings, diagnostics: DiagnosticsCollector
    ) -> None:
        scanner = RepositoryScanner(settings, diagnostics)
        result = scanner.scan()
        for files in result.values():
            for f in files:
                assert "__pycache__" not in str(f)
