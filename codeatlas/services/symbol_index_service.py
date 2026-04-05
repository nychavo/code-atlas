"""Symbol index service — builds a SymbolIndex from a list of Artifacts."""

import logging
from datetime import datetime, timezone

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.core.enums import SymbolKind
from codeatlas.models.artifact_models import Artifact
from codeatlas.models.symbol_models import SymbolEntry, SymbolIndex
from codeatlas.utils.symbol_id_helper import SymbolIdHelper


class SymbolIndexService:
    """Builds a project-wide symbol index from analyzed artifacts."""

    def __init__(self, settings: Settings, diagnostics: DiagnosticsCollector) -> None:
        self.settings = settings
        self.diagnostics = diagnostics
        self.logger = logging.getLogger(__name__)

    def build(self, artifacts: list[Artifact]) -> SymbolIndex:
        """Build and return a :class:`~codeatlas.models.symbol_models.SymbolIndex`."""
        symbols: dict[str, SymbolEntry] = {}

        for artifact in artifacts:
            for cls in artifact.classes:
                entry = SymbolEntry(
                    symbol_id=cls.class_id,
                    name=cls.name,
                    qualified_name=cls.qualified_name,
                    kind=SymbolKind.CLASS.value,
                    language=artifact.language,
                    owning_artifact=artifact.artifact_id,
                    path=artifact.path,
                    line_number=cls.line_start,
                    is_public=not cls.name.startswith("_"),
                )
                symbols[cls.class_id] = entry

                for method in cls.methods:
                    m_entry = SymbolEntry(
                        symbol_id=method.method_id,
                        name=method.name,
                        qualified_name=method.qualified_name,
                        kind=SymbolKind.METHOD.value,
                        language=artifact.language,
                        owning_artifact=artifact.artifact_id,
                        path=artifact.path,
                        line_number=method.line_start,
                        is_public=not method.name.startswith("_"),
                    )
                    symbols[method.method_id] = m_entry

            for fn in artifact.functions:
                entry = SymbolEntry(
                    symbol_id=fn.function_id,
                    name=fn.name,
                    qualified_name=fn.qualified_name,
                    kind=SymbolKind.FUNCTION.value,
                    language=artifact.language,
                    owning_artifact=artifact.artifact_id,
                    path=artifact.path,
                    line_number=fn.line_start,
                    is_public=not fn.name.startswith("_"),
                )
                symbols[fn.function_id] = entry

            for const in artifact.constants:
                entry = SymbolEntry(
                    symbol_id=const.constant_id,
                    name=const.name,
                    qualified_name=f"{artifact.module_name}.{const.name}",
                    kind=SymbolKind.CONSTANT.value,
                    language=artifact.language,
                    owning_artifact=artifact.artifact_id,
                    path=artifact.path,
                    line_number=const.line_number,
                    is_public=True,
                )
                symbols[const.constant_id] = entry

        self.logger.info("Built symbol index with %d entries", len(symbols))
        return SymbolIndex(
            schema_version=self.settings.schema_version,
            project_id=self.settings.project_id,
            symbols=symbols,
            metadata={
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_symbols": len(symbols),
            },
        )
