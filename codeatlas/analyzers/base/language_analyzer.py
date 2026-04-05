"""Abstract base class for language analyzers."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from codeatlas.models.artifact_models import Artifact


class BaseLanguageAnalyzer(ABC):
    """Abstract base for all language-specific analyzers."""

    def __init__(self, settings, diagnostics) -> None:
        self.settings = settings
        self.diagnostics = diagnostics
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def analyze(self, file_path: Path) -> Artifact | None:
        """Analyse *file_path* and return an Artifact, or None on failure."""
        ...

    @property
    @abstractmethod
    def language(self) -> str:
        """Return the lower-case name of the language handled by this analyzer."""
        ...
