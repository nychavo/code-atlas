"""Python dependency extractor — builds DependencyRecord objects from resolved AST data."""

import logging
from pathlib import Path
from typing import Any

from codeatlas.analyzers.base.dependency_extractor import BaseDependencyExtractor
from codeatlas.core.enums import DependencyKind
from codeatlas.models.artifact_models import DependencyRecord
from codeatlas.utils.confidence_helper import ConfidenceHelper
from codeatlas.utils.module_name_helper import ModuleNameHelper
from codeatlas.utils.symbol_id_helper import SymbolIdHelper


class PythonDependencyExtractor(BaseDependencyExtractor):
    """Extracts dependency records from resolved Python AST structure data."""

    def __init__(self, root_path: Path, settings: Any) -> None:
        self.root_path = root_path
        self.settings = settings
        self.logger = logging.getLogger(__name__)

    def extract_dependencies(
        self, file_path: Path, raw_structure: dict[str, Any]
    ) -> list[DependencyRecord]:
        """Return a list of DependencyRecord objects derived from *raw_structure*."""
        deps: list[DependencyRecord] = []
        module_name = ModuleNameHelper.derive_module_name(file_path, self.root_path)

        deps.extend(self._import_dependencies(module_name, raw_structure))
        deps.extend(self._inheritance_dependencies(module_name, raw_structure))

        return deps

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _import_dependencies(
        self, module_name: str, raw_structure: dict[str, Any]
    ) -> list[DependencyRecord]:
        deps: list[DependencyRecord] = []
        for imp in raw_structure.get("imports", []):
            target_module = imp.get("module", "")
            dep_id = SymbolIdHelper.generate_dependency_id(
                module_name, target_module, DependencyKind.IMPORTS.value
            )
            deps.append(
                DependencyRecord(
                    dependency_id=dep_id,
                    kind=DependencyKind.IMPORTS.value,
                    source=module_name,
                    target=target_module,
                    target_module=target_module,
                    confidence=imp.get("confidence", ConfidenceHelper.DEFAULT_HIGH),
                    line_number=imp.get("line_number"),
                    evidence=f"import {target_module}",
                    is_resolved=imp.get("is_resolved", True),
                )
            )
        return deps

    def _inheritance_dependencies(
        self, module_name: str, raw_structure: dict[str, Any]
    ) -> list[DependencyRecord]:
        deps: list[DependencyRecord] = []
        for cls in raw_structure.get("classes", []):
            for base in cls.get("base_classes", []):
                if base in ("object",):
                    continue
                dep_id = SymbolIdHelper.generate_dependency_id(
                    f"{module_name}.{cls['name']}", base, DependencyKind.INHERITS_FROM.value
                )
                deps.append(
                    DependencyRecord(
                        dependency_id=dep_id,
                        kind=DependencyKind.INHERITS_FROM.value,
                        source=f"{module_name}.{cls['name']}",
                        target=base,
                        target_module=None,
                        confidence=ConfidenceHelper.score_base_class(is_resolved=False),
                        line_number=cls.get("line_start"),
                        evidence=f"class {cls['name']}({base})",
                        is_resolved=False,
                    )
                )
        return deps
