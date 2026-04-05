"""Pydantic models for project manifest data."""

from pydantic import BaseModel


class ArtifactEntry(BaseModel):
    """Entry describing a single artifact in the manifest."""

    artifact_id: str
    path: str
    module_name: str
    language: str
    artifact_file: str


class Manifest(BaseModel):
    """Project manifest that describes all generated artifacts and output files."""

    schema_version: str
    project_id: str
    project_name: str
    root_path: str
    artifact_directory: str
    graph_file: str
    symbol_index_file: str
    manifest_file: str
    entry_points: list[str]
    artifacts: list[ArtifactEntry]
    total_files: int
    total_artifacts: int
    languages: list[str]
    created_at: str
    metadata: dict
