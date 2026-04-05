"""Repository scanner — discovers files and groups them by language."""

import logging
from pathlib import Path

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.services.file_discovery_service import FileDiscoveryService
from codeatlas.services.language_detection_service import LanguageDetectionService


class RepositoryScanner:
    """Scans a repository and returns discovered files grouped by language."""

    def __init__(self, settings: Settings, diagnostics: DiagnosticsCollector) -> None:
        self.settings = settings
        self.diagnostics = diagnostics
        self.file_discovery = FileDiscoveryService(settings)
        self.lang_detection = LanguageDetectionService()
        self.logger = logging.getLogger(__name__)

    def scan(self) -> dict[str, list[Path]]:
        """Return a mapping of language name → list of discovered file paths."""
        files = self.file_discovery.discover()
        grouped: dict[str, list[Path]] = {}
        for file_path in files:
            lang = self.lang_detection.detect(file_path)
            grouped.setdefault(lang, []).append(file_path)
        self.logger.info(
            "Scan complete: %d files across %d languages",
            len(files),
            len(grouped),
        )
        return grouped
