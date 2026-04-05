"""Pydantic models for dependency graph data."""

from pydantic import BaseModel


class DependencyEdge(BaseModel):
    """A directed edge in the dependency graph."""

    edge_id: str
    source_artifact: str
    target_artifact: str | None
    target_module: str
    kind: str
    confidence: float
    is_external: bool
    is_stdlib: bool
    line_number: int | None


class SymbolEdge(BaseModel):
    """A directed edge between two symbols."""

    edge_id: str
    source_symbol: str
    target_symbol: str
    kind: str
    confidence: float


class ArchitectureSummary(BaseModel):
    """Summary of architectural analysis results."""

    layer_counts: dict[str, int]
    violations: list[dict]
    cycles: list[list[str]]
    entry_points: list[str]
    external_dependency_count: int


class MasterDependencyGraph(BaseModel):
    """The master dependency graph for an entire project."""

    schema_version: str
    project_id: str
    root_path: str
    artifacts: list[str]
    dependency_edges: list[DependencyEdge]
    symbol_edges: list[SymbolEdge]
    entry_points: list[str]
    cycles: list[list[str]]
    external_dependencies: list[str]
    architecture_summary: ArchitectureSummary
    metadata: dict
