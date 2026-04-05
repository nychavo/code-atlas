"""Shared pytest fixtures for the CodeAtlas test suite."""

from pathlib import Path

import pytest

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector


@pytest.fixture()
def sample_project_path() -> Path:
    """Return the absolute path to the sample project directory."""
    return Path(__file__).parent / "sample_project"


@pytest.fixture()
def tmp_output_dir(tmp_path: Path) -> Path:
    """Return a temporary output directory."""
    out = tmp_path / "codeatlas_output"
    out.mkdir()
    return out


@pytest.fixture()
def settings(sample_project_path: Path, tmp_output_dir: Path) -> Settings:
    """Return a Settings instance pointing at the sample project."""
    return Settings(
        project_id="test_project",
        project_name="Test Project",
        root_path=sample_project_path,
        output_dir=tmp_output_dir,
    )


@pytest.fixture()
def diagnostics() -> DiagnosticsCollector:
    """Return a fresh DiagnosticsCollector."""
    return DiagnosticsCollector()
