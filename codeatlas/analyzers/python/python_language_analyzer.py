"""Top-level Python language analyzer that orchestrates all Python sub-components."""

from pathlib import Path

from codeatlas.analyzers.base.language_analyzer import BaseLanguageAnalyzer
from codeatlas.analyzers.python.python_ast_extractor import PythonAstExtractor
from codeatlas.analyzers.python.python_artifact_builder import PythonArtifactBuilder
from codeatlas.analyzers.python.python_dependency_extractor import PythonDependencyExtractor
from codeatlas.analyzers.python.python_summary_generator import PythonSummaryGenerator
from codeatlas.analyzers.python.python_symbol_resolver import PythonSymbolResolver
from codeatlas.models.artifact_models import Artifact
from codeatlas.utils.module_name_helper import ModuleNameHelper


class PythonLanguageAnalyzer(BaseLanguageAnalyzer):
    """Orchestrates the full analysis pipeline for a Python source file."""

    @property
    def language(self) -> str:
        """Return the language identifier handled by this analyzer."""
        return "python"

    def __init__(self, settings, diagnostics) -> None:
        super().__init__(settings, diagnostics)
        self.extractor = PythonAstExtractor()
        self.resolver = PythonSymbolResolver(
            settings.root_path, settings.analyzer_config.use_jedi
        )
        self.dep_extractor = PythonDependencyExtractor(settings.root_path, settings)
        self.artifact_builder = PythonArtifactBuilder(settings, settings.project_id)
        self.summary_generator = PythonSummaryGenerator()

    def analyze(self, file_path: Path) -> Artifact | None:
        """Analyse *file_path* and return an :class:`~codeatlas.models.artifact_models.Artifact`.

        Returns None if the file cannot be parsed or analysis fails.
        """
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            raw = self.extractor.extract(file_path, source)

            if "error" in raw:
                self.diagnostics.add_error(
                    f"Parse error in {file_path}: {raw['error']}",
                    file_path=str(file_path),
                )
                return None

            resolved = self.resolver.resolve(file_path, raw)

            module_name = ModuleNameHelper.derive_module_name(file_path, self.settings.root_path)
            summary = self.summary_generator.generate_summary(
                {**resolved, "path": str(file_path), "module_name": module_name},
                self.settings,
            )
            resolved["summary"] = summary

            deps = self.dep_extractor.extract_dependencies(file_path, resolved)
            artifact = self.artifact_builder.build(file_path, resolved, deps)
            return artifact

        except Exception as exc:  # noqa: BLE001
            self.diagnostics.add_error(
                f"Analysis failed for {file_path}: {exc}",
                file_path=str(file_path),
            )
            self.logger.exception("Failed to analyse %s", file_path)
            return None
