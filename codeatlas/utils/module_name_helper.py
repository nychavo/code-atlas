"""Module name derivation helpers."""

from pathlib import Path


class ModuleNameHelper:
    """Static utility methods for deriving Python dotted module names."""

    @staticmethod
    def derive_module_name(file_path: Path, root_path: Path) -> str:
        """Convert a file path to a dotted Python module name.

        For example, ``root/foo/bar.py`` relative to ``root`` becomes
        ``foo.bar``.  ``root/foo/__init__.py`` becomes ``foo``.
        """
        try:
            rel = file_path.resolve().relative_to(root_path.resolve())
        except ValueError:
            # Fall back to using the stem of the filename alone
            return file_path.stem

        parts = list(rel.parts)
        if not parts:
            return ""

        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        elif parts[-1].endswith(".py"):
            parts[-1] = parts[-1][:-3]

        return ".".join(parts) if parts else ""

    @staticmethod
    def is_package_init(path: Path) -> bool:
        """Return True if *path* is a package ``__init__.py``."""
        return path.name == "__init__.py"

    @staticmethod
    def normalize_module_name(name: str) -> str:
        """Normalise a module name by lower-casing and stripping whitespace."""
        return name.strip().lower()
