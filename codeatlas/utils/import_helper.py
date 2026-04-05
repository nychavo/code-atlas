"""Import classification helpers."""

import sys


class ImportHelper:
    """Static utility methods for classifying Python import statements."""

    STDLIB_MODULES: set[str] = set(sys.stdlib_module_names)

    @staticmethod
    def is_stdlib(module_name: str) -> bool:
        """Return True if the top-level package of *module_name* is a stdlib module."""
        top_level = module_name.split(".")[0].lstrip(".")
        return top_level in ImportHelper.STDLIB_MODULES

    @staticmethod
    def is_relative(module_name: str) -> bool:
        """Return True if *module_name* represents a relative import (starts with dot)."""
        return module_name.startswith(".")

    @staticmethod
    def normalize_import(module: str, names: list[str]) -> str:
        """Return a human-readable import representation."""
        if names and names != [module]:
            return f"from {module} import {', '.join(names)}"
        return f"import {module}"

    @staticmethod
    def split_module_path(module: str) -> list[str]:
        """Split a dotted module path into its component parts."""
        return [part for part in module.split(".") if part]
