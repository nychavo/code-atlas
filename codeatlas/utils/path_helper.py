"""Path manipulation helpers."""

import fnmatch
from pathlib import Path
from typing import Iterator


class PathHelper:
    """Static utility methods for path operations."""

    @staticmethod
    def normalize_path(path: Path | str) -> Path:
        """Resolve and normalise a path to an absolute Path."""
        return Path(path).resolve()

    @staticmethod
    def make_relative(path: Path, root: Path) -> Path:
        """Return *path* relative to *root*, resolving both first."""
        return path.resolve().relative_to(root.resolve())

    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """Create directory (and parents) if it does not exist; return *path*."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_artifact_filename(artifact_id: str) -> str:
        """Return the JSON filename for an artifact ID."""
        safe = artifact_id.replace(":", "_").replace("/", "_").replace("\\", "_")
        return f"{safe}.json"

    @staticmethod
    def is_excluded(path: Path, patterns: list[str]) -> bool:
        """Return True if *path* matches any of the given fnmatch *patterns*."""
        path_str = str(path).replace("\\", "/")
        for pattern in patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
        return False

    @staticmethod
    def iter_source_files(
        root: Path,
        extensions: set[str],
        exclude_patterns: list[str],
    ) -> Iterator[Path]:
        """Yield source files under *root* matching *extensions*, excluding patterns."""
        for file_path in sorted(root.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in extensions:
                continue
            try:
                rel = file_path.relative_to(root)
            except ValueError:
                continue
            rel_str = str(rel).replace("\\", "/")
            if not any(fnmatch.fnmatch(rel_str, pat) for pat in exclude_patterns):
                yield file_path
