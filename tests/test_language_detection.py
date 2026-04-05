"""Tests for LanguageDetectionService."""

from pathlib import Path

import pytest

from codeatlas.services.language_detection_service import LanguageDetectionService


@pytest.fixture()
def service() -> LanguageDetectionService:
    return LanguageDetectionService()


class TestLanguageDetectionService:
    def test_detect_python(self, service: LanguageDetectionService) -> None:
        assert service.detect(Path("foo/bar.py")) == "python"

    def test_detect_python_stub(self, service: LanguageDetectionService) -> None:
        assert service.detect(Path("foo/bar.pyi")) == "python"

    def test_detect_javascript(self, service: LanguageDetectionService) -> None:
        assert service.detect(Path("app.js")) == "javascript"

    def test_detect_typescript(self, service: LanguageDetectionService) -> None:
        assert service.detect(Path("index.ts")) == "typescript"

    def test_detect_unknown(self, service: LanguageDetectionService) -> None:
        assert service.detect(Path("readme.md")) == "unknown"

    def test_is_supported_true(self, service: LanguageDetectionService) -> None:
        assert service.is_supported(Path("module.py"), ["python"]) is True

    def test_is_supported_false(self, service: LanguageDetectionService) -> None:
        assert service.is_supported(Path("index.ts"), ["python"]) is False
