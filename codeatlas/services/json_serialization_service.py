"""JSON serialisation service for artifacts and other output models."""

import logging
from pathlib import Path

from codeatlas.config.settings import Settings
from codeatlas.models.artifact_models import Artifact
from codeatlas.models.graph_models import MasterDependencyGraph
from codeatlas.models.manifest_models import Manifest
from codeatlas.models.symbol_models import SymbolIndex
from codeatlas.utils.json_helper import JsonHelper
from codeatlas.utils.path_helper import PathHelper


class JsonSerializationService:
    """Writes and reads CodeAtlas output models to/from JSON files."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self._artifact_dir = settings.output_dir / "artifacts"
        PathHelper.ensure_dir(self._artifact_dir)

    def write_artifact(self, artifact: Artifact) -> Path:
        """Serialise *artifact* to a JSON file; return the written path."""
        filename = PathHelper.get_artifact_filename(artifact.artifact_id)
        out_path = self._artifact_dir / filename
        JsonHelper.write_model(artifact, out_path)
        self.logger.debug("Wrote artifact to %s", out_path)
        return out_path

    def read_artifact(self, path: Path) -> Artifact:
        """Deserialise an Artifact from *path*."""
        return JsonHelper.read_model(path, Artifact)

    def write_graph(self, graph: MasterDependencyGraph) -> Path:
        """Write the master dependency graph to the output directory."""
        out_path = self.settings.output_dir / "master_dependency_graph.json"
        JsonHelper.write_model(graph, out_path)
        return out_path

    def write_symbol_index(self, index: SymbolIndex) -> Path:
        """Write the symbol index to the output directory."""
        out_path = self.settings.output_dir / "symbol_index.json"
        JsonHelper.write_model(index, out_path)
        return out_path

    def write_manifest(self, manifest: Manifest) -> Path:
        """Write the manifest to the output directory."""
        out_path = self.settings.output_dir / "manifest.json"
        JsonHelper.write_model(manifest, out_path)
        return out_path
