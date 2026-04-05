"""Resolves Python module paths to filesystem paths."""

from pathlib import Path


class PythonModuleResolver:
    """Builds and queries a map of dotted module names to file paths."""

    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path
        self._module_map: dict[str, Path] = {}
        self._build_module_map()

    def _build_module_map(self) -> None:
        """Walk *root_path* and populate the internal module→path mapping."""
        for py_file in self.root_path.rglob("*.py"):
            try:
                rel = py_file.relative_to(self.root_path)
            except ValueError:
                continue
            parts = list(rel.parts)
            if parts[-1] == "__init__.py":
                parts = parts[:-1]
            elif parts[-1].endswith(".py"):
                parts[-1] = parts[-1][:-3]
            if parts:
                module = ".".join(parts)
                self._module_map[module] = py_file

    def resolve_module(self, module_name: str) -> Path | None:
        """Return the file path for *module_name*, or None if unknown."""
        return self._module_map.get(module_name)

    def get_module_map(self) -> dict[str, Path]:
        """Return a copy of the full module→path mapping."""
        return dict(self._module_map)
