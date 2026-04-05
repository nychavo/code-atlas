"""Graph builder — constructs dependency and symbol edges from artifacts."""

from codeatlas.core.enums import DependencyKind
from codeatlas.models.artifact_models import Artifact
from codeatlas.models.graph_models import DependencyEdge, SymbolEdge
from codeatlas.utils.import_helper import ImportHelper
from codeatlas.utils.symbol_id_helper import SymbolIdHelper


class GraphBuilder:
    """Builds edge lists for the master dependency graph."""

    def __init__(
        self,
        artifacts: list[Artifact],
        module_to_artifact: dict[str, str],
    ) -> None:
        self.artifacts = artifacts
        self.module_to_artifact = module_to_artifact

    def build_dependency_edges(self) -> list[DependencyEdge]:
        """Return all dependency edges derived from artifact dependency records."""
        edges: list[DependencyEdge] = []
        for artifact in self.artifacts:
            for dep in artifact.dependencies:
                target_artifact = self.module_to_artifact.get(dep.target)
                is_stdlib = ImportHelper.is_stdlib(dep.target.lstrip(".")) if dep.target else False
                is_external = (
                    target_artifact is None
                    and not dep.target.startswith(".")
                    and not is_stdlib
                )
                edge_id = SymbolIdHelper.generate_dependency_id(
                    dep.source, dep.target, dep.kind
                )
                edges.append(
                    DependencyEdge(
                        edge_id=edge_id,
                        source_artifact=artifact.artifact_id,
                        target_artifact=target_artifact,
                        target_module=dep.target,
                        kind=dep.kind,
                        confidence=dep.confidence,
                        is_external=is_external,
                        is_stdlib=is_stdlib,
                        line_number=dep.line_number,
                    )
                )
        return edges

    def build_symbol_edges(self) -> list[SymbolEdge]:
        """Return symbol-level edges derived from inheritance relationships."""
        edges: list[SymbolEdge] = []
        for artifact in self.artifacts:
            for cls in artifact.classes:
                for i, base in enumerate(cls.resolved_base_classes):
                    if base in ("object",):
                        continue
                    edge_id = SymbolIdHelper.generate_dependency_id(
                        cls.class_id, base, DependencyKind.INHERITS_FROM.value
                    )
                    edges.append(
                        SymbolEdge(
                            edge_id=edge_id,
                            source_symbol=cls.class_id,
                            target_symbol=base,
                            kind=DependencyKind.INHERITS_FROM.value,
                            confidence=0.6,
                        )
                    )
        return edges
