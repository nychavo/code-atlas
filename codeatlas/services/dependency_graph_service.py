"""Dependency graph service — builds MasterDependencyGraph from artifacts."""

import logging
from datetime import datetime, timezone

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.core.enums import DependencyKind
from codeatlas.graph.cycle_detector import CycleDetector
from codeatlas.graph.graph_builder import GraphBuilder
from codeatlas.models.artifact_models import Artifact
from codeatlas.models.graph_models import ArchitectureSummary, MasterDependencyGraph
from codeatlas.utils.import_helper import ImportHelper
from codeatlas.utils.symbol_id_helper import SymbolIdHelper


class DependencyGraphService:
    """Builds and analyses the master dependency graph for a project."""

    def __init__(self, settings: Settings, diagnostics: DiagnosticsCollector) -> None:
        self.settings = settings
        self.diagnostics = diagnostics
        self.logger = logging.getLogger(__name__)

    def build(self, artifacts: list[Artifact]) -> MasterDependencyGraph:
        """Build a :class:`~codeatlas.models.graph_models.MasterDependencyGraph` from *artifacts*."""
        artifact_ids = [a.artifact_id for a in artifacts]
        module_to_artifact: dict[str, str] = {a.module_name: a.artifact_id for a in artifacts}

        builder = GraphBuilder(artifacts, module_to_artifact)
        dep_edges = builder.build_dependency_edges()
        symbol_edges = builder.build_symbol_edges()

        # Detect cycles in import graph
        import_graph: dict[str, list[str]] = {}
        for edge in dep_edges:
            if edge.kind == DependencyKind.IMPORTS.value and not edge.is_external:
                import_graph.setdefault(edge.source_artifact, []).append(
                    edge.target_artifact or edge.target_module
                )
        cycles = CycleDetector.detect(import_graph)

        # Collect external dependencies
        external_deps: list[str] = sorted(
            set(
                edge.target_module
                for edge in dep_edges
                if edge.is_external or edge.is_stdlib
            )
        )

        # Layer counts
        layer_counts: dict[str, int] = {}
        for artifact in artifacts:
            layer = artifact.summary.architectural_layer
            layer_counts[layer] = layer_counts.get(layer, 0) + 1

        arch_summary = ArchitectureSummary(
            layer_counts=layer_counts,
            violations=[],
            cycles=cycles,
            entry_points=[],
            external_dependency_count=len(external_deps),
        )

        return MasterDependencyGraph(
            schema_version=self.settings.schema_version,
            project_id=self.settings.project_id,
            root_path=str(self.settings.root_path),
            artifacts=artifact_ids,
            dependency_edges=dep_edges,
            symbol_edges=symbol_edges,
            entry_points=[],
            cycles=cycles,
            external_dependencies=external_deps,
            architecture_summary=arch_summary,
            metadata={
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_edges": len(dep_edges),
            },
        )
