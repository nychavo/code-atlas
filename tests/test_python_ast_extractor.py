"""Tests for PythonAstExtractor."""

from pathlib import Path

import pytest

from codeatlas.analyzers.python.python_ast_extractor import PythonAstExtractor


@pytest.fixture()
def extractor() -> PythonAstExtractor:
    return PythonAstExtractor()


class TestPythonAstExtractor:
    def test_extract_docstring(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = '"""Module docstring."""\n'
        f = tmp_path / "mod.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        assert result["docstring"] == "Module docstring."

    def test_extract_imports(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = "import os\nfrom pathlib import Path\n"
        f = tmp_path / "mod.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        modules = {imp["module"] for imp in result["imports"]}
        assert "os" in modules
        assert "pathlib" in modules

    def test_extract_class(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = "class Foo:\n    def bar(self) -> None:\n        pass\n"
        f = tmp_path / "mod.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "Foo"
        assert result["classes"][0]["methods"][0]["name"] == "bar"

    def test_extract_function(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = "def greet(name: str) -> str:\n    return f'Hello {name}'\n"
        f = tmp_path / "mod.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        assert len(result["functions"]) == 1
        fn = result["functions"][0]
        assert fn["name"] == "greet"
        assert fn["return_annotation"] == "str"
        params = {p["name"] for p in fn["parameters"]}
        assert "name" in params

    def test_extract_constants(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = "MAX_SIZE: int = 100\n"
        f = tmp_path / "mod.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        assert any(c["name"] == "MAX_SIZE" for c in result["constants"])

    def test_extract_async_function(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = "async def fetch() -> None:\n    pass\n"
        f = tmp_path / "mod.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        assert result["functions"][0]["is_async"] is True

    def test_extract_base_classes(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = "from pydantic import BaseModel\nclass User(BaseModel):\n    name: str\n"
        f = tmp_path / "mod.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        assert "BaseModel" in result["classes"][0]["base_classes"]

    def test_syntax_error_returns_error_key(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = "def bad syntax:\n"
        f = tmp_path / "bad.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        assert "error" in result

    def test_file_stats(self, extractor: PythonAstExtractor, tmp_path: Path) -> None:
        src = "# comment\n\ncode = 1\n"
        f = tmp_path / "mod.py"
        f.write_text(src)
        result = extractor.extract(f, src)
        stats = result["file_stats"]
        assert stats["line_count"] == 3
        assert stats["blank_line_count"] == 1
        assert stats["comment_line_count"] == 1

    def test_extract_sample_project_models(
        self, extractor: PythonAstExtractor, sample_project_path: Path
    ) -> None:
        models_file = sample_project_path / "models.py"
        src = models_file.read_text()
        result = extractor.extract(models_file, src)
        class_names = {c["name"] for c in result["classes"]}
        assert "User" in class_names
        assert "Product" in class_names
