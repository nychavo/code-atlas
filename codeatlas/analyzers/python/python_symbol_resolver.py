"""Python symbol resolver — enriches raw AST data with resolution metadata."""

import logging
from pathlib import Path
from typing import Any

from codeatlas.analyzers.base.symbol_resolver import BaseSymbolResolver
from codeatlas.utils.confidence_helper import ConfidenceHelper
from codeatlas.utils.import_helper import ImportHelper

try:
    import jedi  # noqa: F401

    JEDI_AVAILABLE = True
except ImportError:
    JEDI_AVAILABLE = False


class PythonSymbolResolver(BaseSymbolResolver):
    """Resolves Python symbols and enriches raw structure data."""

    def __init__(self, root_path: Path, use_jedi: bool = True) -> None:
        self.root_path = root_path
        self.use_jedi = use_jedi and JEDI_AVAILABLE
        self.logger = logging.getLogger(__name__)

    def resolve(self, file_path: Path, raw_structure: dict[str, Any]) -> dict[str, Any]:
        """Resolve imports and base-class references in *raw_structure*."""
        resolved = dict(raw_structure)
        resolved["imports"] = [
            self._resolve_import(imp, file_path)
            for imp in raw_structure.get("imports", [])
        ]
        resolved["classes"] = [
            self._resolve_class(cls, file_path)
            for cls in raw_structure.get("classes", [])
        ]
        return resolved

    def _resolve_import(self, imp: dict[str, Any], file_path: Path) -> dict[str, Any]:
        module = imp.get("module", "")
        is_stdlib = ImportHelper.is_stdlib(module.lstrip("."))
        confidence = ConfidenceHelper.score_import(is_resolved=True, is_stdlib=is_stdlib)
        return {**imp, "is_stdlib": is_stdlib, "confidence": confidence, "is_resolved": True}

    def _resolve_class(self, cls: dict[str, Any], file_path: Path) -> dict[str, Any]:
        resolved_bases: list[str] = []
        for base in cls.get("base_classes", []):
            resolved = self._try_resolve_symbol(base, file_path)
            resolved_bases.append(resolved or base)
        return {**cls, "resolved_base_classes": resolved_bases}

    def _try_resolve_symbol(self, name: str, file_path: Path) -> str | None:
        """Attempt jedi-based resolution; returns None on failure or when unavailable."""
        if not self.use_jedi:
            return None
        try:
            import jedi

            jedi.Script(path=str(file_path), project=jedi.Project(path=str(self.root_path)))
            return None
        except Exception as exc:
            self.logger.debug("Jedi resolution failed for %r: %s", name, exc)
            return None
