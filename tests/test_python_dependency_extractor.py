"""Tests for PythonDependencyExtractor."""

from pathlib import Path

import pytest

from codeatlas.analyzers.python.python_dependency_extractor import PythonDependencyExtractor
from codeatlas.config.settings import Settings
from codeatlas.core.enums import DependencyKind


@pytest.fixture()
def extractor(settings: Settings) -> PythonDependencyExtractor:
    return PythonDependencyExtractor(settings.root_path, settings)


class TestPythonDependencyExtractor:
    def test_extracts_import_dependency(
        self, extractor: PythonDependencyExtractor, sample_project_path: Path
    ) -> None:
        raw = {
            "imports": [
                {
                    "module": "os",
                    "names": ["os"],
                    "alias": None,
                    "is_from_import": False,
                    "is_relative": False,
                    "is_stdlib": True,
                    "is_resolved": True,
                    "confidence": 0.95,
                    "line_number": 1,
                }
            ],
            "classes": [],
        }
        file_path = sample_project_path / "utils.py"
        deps = extractor.extract_dependencies(file_path, raw)
        assert any(d.kind == DependencyKind.IMPORTS.value for d in deps)
        assert any(d.target == "os" for d in deps)

    def test_extracts_inheritance_dependency(
        self, extractor: PythonDependencyExtractor, sample_project_path: Path
    ) -> None:
        raw = {
            "imports": [],
            "classes": [
                {
                    "name": "Child",
                    "base_classes": ["Parent"],
                    "resolved_base_classes": ["Parent"],
                    "line_start": 5,
                }
            ],
        }
        file_path = sample_project_path / "models.py"
        deps = extractor.extract_dependencies(file_path, raw)
        inh = [d for d in deps if d.kind == DependencyKind.INHERITS_FROM.value]
        assert len(inh) == 1
        assert inh[0].target == "Parent"

    def test_no_object_base_dependency(
        self, extractor: PythonDependencyExtractor, sample_project_path: Path
    ) -> None:
        raw = {
            "imports": [],
            "classes": [{"name": "Foo", "base_classes": ["object"], "line_start": 1}],
        }
        file_path = sample_project_path / "models.py"
        deps = extractor.extract_dependencies(file_path, raw)
        inh = [d for d in deps if d.kind == DependencyKind.INHERITS_FROM.value]
        assert len(inh) == 0
