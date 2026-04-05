"""Service that discovers source files within a project root."""

import fnmatch
import logging
from pathlib import Path

from codeatlas.config.settings import Settings


class FileDiscoveryService:
    """Discovers source files under the configured root path."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = logging.getLogger(__name__)

    def discover(self) -> list[Path]:
        """Return sorted list of source files that pass the exclude filters."""
        root = self.settings.root_path
        exclude = self.settings.exclude_patterns
        result: list[Path] = []

        for py_file in root.rglob("*.py"):
            try:
                rel = py_file.relative_to(root)
            except ValueError:
                continue
            rel_str = str(rel).replace("\\", "/")
            if not any(fnmatch.fnmatch(rel_str, pat) for pat in exclude):
                result.append(py_file)

        self.logger.info("Discovered %d source files under %s", len(result), root)
        return sorted(result)
