"""Analyzer factory that wires together the registry and individual analyzers."""

from pathlib import Path

from codeatlas.analyzers.base.language_analyzer import BaseLanguageAnalyzer
from codeatlas.analyzers.registry import LanguageRegistry
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.core.exceptions import LanguageNotSupportedError
from codeatlas.models.artifact_models import Artifact


class AnalyzerFactory:
    """Creates and caches language analyzer instances."""

    def __init__(self, settings, diagnostics: DiagnosticsCollector) -> None:
        self.settings = settings
        self.diagnostics = diagnostics
        self._cache: dict[str, BaseLanguageAnalyzer] = {}
        self._register_defaults()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _register_defaults(self) -> None:
        """Ensure built-in analyzers are registered."""
        if not LanguageRegistry.is_supported("python"):
            from codeatlas.analyzers.python.python_language_analyzer import PythonLanguageAnalyzer

            LanguageRegistry.register("python", PythonLanguageAnalyzer)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_analyzer(self, language: str) -> BaseLanguageAnalyzer:
        """Return a (cached) analyzer instance for *language*.

        Raises :class:`~codeatlas.core.exceptions.LanguageNotSupportedError`
        if the language is not registered.
        """
        lang = language.lower()
        if lang not in self._cache:
            analyzer_class = LanguageRegistry.get(lang)
            if analyzer_class is None:
                raise LanguageNotSupportedError(lang)
            self._cache[lang] = analyzer_class(self.settings, self.diagnostics)
        return self._cache[lang]

    def analyze_file(self, file_path: Path, language: str) -> Artifact | None:
        """Analyse *file_path* using the appropriate analyzer for *language*.

        Returns None if the language is unsupported or analysis fails.
        """
        try:
            analyzer = self.get_analyzer(language)
        except LanguageNotSupportedError:
            self.diagnostics.add_warning(
                f"No analyzer available for language {language!r}; skipping {file_path}",
                file_path=str(file_path),
            )
            return None
        return analyzer.analyze(file_path)
