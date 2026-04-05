"""Tests for PythonSymbolResolver."""

from pathlib import Path

import pytest

from codeatlas.analyzers.python.python_symbol_resolver import PythonSymbolResolver


@pytest.fixture()
def resolver(sample_project_path: Path) -> PythonSymbolResolver:
    return PythonSymbolResolver(sample_project_path, use_jedi=False)


class TestPythonSymbolResolver:
    def test_resolve_marks_stdlib(self, resolver: PythonSymbolResolver, tmp_path: Path) -> None:
        raw = {
            "imports": [{"module": "os", "names": ["os"], "alias": None, "is_from_import": False, "is_relative": False, "line_number": 1}],
            "classes": [],
        }
        resolved = resolver.resolve(tmp_path / "mod.py", raw)
        assert resolved["imports"][0]["is_stdlib"] is True

    def test_resolve_marks_third_party(self, resolver: PythonSymbolResolver, tmp_path: Path) -> None:
        raw = {
            "imports": [{"module": "pydantic", "names": ["BaseModel"], "alias": None, "is_from_import": True, "is_relative": False, "line_number": 1}],
            "classes": [],
        }
        resolved = resolver.resolve(tmp_path / "mod.py", raw)
        assert resolved["imports"][0]["is_stdlib"] is False

    def test_resolve_adds_resolved_base_classes(self, resolver: PythonSymbolResolver, tmp_path: Path) -> None:
        raw = {
            "imports": [],
            "classes": [
                {
                    "name": "Foo",
                    "base_classes": ["Bar"],
                    "methods": [],
                    "decorators": [],
                    "docstring": None,
                    "class_variables": [],
                    "instance_variables": [],
                    "line_start": 1,
                    "line_end": 5,
                    "is_dataclass": False,
                    "is_abstract": False,
                }
            ],
        }
        resolved = resolver.resolve(tmp_path / "mod.py", raw)
        assert "resolved_base_classes" in resolved["classes"][0]
