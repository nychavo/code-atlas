"""File-extension-based language detection service."""

from pathlib import Path

EXTENSION_MAP: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".c": "c",
    ".h": "c",
    ".cs": "csharp",
}


class LanguageDetectionService:
    """Detects the programming language of a file from its extension."""

    def detect(self, path: Path) -> str:
        """Return the language name for *path*, or ``'unknown'`` if unrecognised."""
        return EXTENSION_MAP.get(path.suffix.lower(), "unknown")

    def is_supported(self, path: Path, supported: list[str]) -> bool:
        """Return True if the detected language is in *supported*."""
        return self.detect(path) in [s.lower() for s in supported]
