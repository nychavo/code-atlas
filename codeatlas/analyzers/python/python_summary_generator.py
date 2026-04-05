"""Python summary generator — derives SummaryRecord from raw artifact data."""

import fnmatch
from typing import Any

from codeatlas.analyzers.base.summary_generator import BaseSummaryGenerator
from codeatlas.core.enums import ArchitecturalLayer
from codeatlas.models.artifact_models import SummaryRecord


class PythonSummaryGenerator(BaseSummaryGenerator):
    """Generates a SummaryRecord for a Python source file."""

    def generate_summary(self, artifact_data: dict[str, Any], settings: Any) -> SummaryRecord:
        """Derive a :class:`~codeatlas.models.artifact_models.SummaryRecord` from *artifact_data*."""
        path = artifact_data.get("path", "")
        layer = self._detect_layer(path, settings)

        exports = [c["name"] for c in artifact_data.get("classes", [])]
        exports += [f["name"] for f in artifact_data.get("functions", [])]

        key_deps = list(
            dict.fromkeys(
                imp.get("module", "")
                for imp in artifact_data.get("imports", [])[:10]
                if imp.get("module")
            )
        )[:5]

        docstring = artifact_data.get("docstring") or ""
        first_line = docstring.split("\n")[0].strip()
        purpose = (
            first_line[:200]
            if first_line
            else f"Python module: {artifact_data.get('module_name', '')}"
        )

        unresolved: list[str] = []
        for cls in artifact_data.get("classes", []):
            for base in cls.get("base_classes", []):
                if base not in ("object", "ABC", "BaseModel") and "." not in base:
                    unresolved.append(f"Unresolved base: {base}")

        return SummaryRecord(
            purpose=purpose,
            architectural_layer=layer,
            key_dependencies=key_deps,
            key_exports=exports[:10],
            unresolved_areas=unresolved[:5],
            complexity_notes=[],
        )

    @staticmethod
    def _detect_layer(path: str, settings: Any) -> str:
        """Return the architectural layer matching *path*, or 'unknown'."""
        normalised = path.replace("\\", "/")
        for lp in settings.layer_patterns:
            for pattern in lp.patterns:
                if fnmatch.fnmatch(normalised, pattern):
                    return lp.layer
        return ArchitecturalLayer.UNKNOWN.value
