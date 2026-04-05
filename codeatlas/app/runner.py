"""CLI entry point for the CodeAtlas analysis tool."""

import logging
import sys
from pathlib import Path

import click

from codeatlas.config.settings import Settings
from codeatlas.core.diagnostics import DiagnosticsCollector
from codeatlas.services.artifact_generation_service import ArtifactGenerationService
from codeatlas.services.dependency_graph_service import DependencyGraphService
from codeatlas.services.json_serialization_service import JsonSerializationService
from codeatlas.services.manifest_generation_service import ManifestGenerationService
from codeatlas.services.repository_scanner import RepositoryScanner
from codeatlas.services.symbol_index_service import SymbolIndexService
from codeatlas.utils.diagnostics_helper import DiagnosticsHelper
from codeatlas.utils.path_helper import PathHelper


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )


@click.command()
@click.argument("root_path", type=click.Path(exists=True))
@click.option("--output-dir", "-o", default="./codeatlas_output", help="Output directory")
@click.option("--project-id", "-p", default="project", help="Project identifier")
@click.option("--project-name", "-n", default="Unknown Project", help="Human-readable project name")
@click.option("--config", "-c", type=click.Path(), default=None, help="Path to codeatlas.yaml config file")
@click.option("--verbose", "-v", is_flag=True, default=False, help="Enable verbose logging")
def main(
    root_path: str,
    output_dir: str,
    project_id: str,
    project_name: str,
    config: str | None,
    verbose: bool,
) -> None:
    """Analyse a code repository and generate CodeAtlas output artefacts.

    ROOT_PATH is the root directory of the project to analyse.
    """
    _configure_logging(verbose)
    logger = logging.getLogger("codeatlas.runner")
    diagnostics = DiagnosticsCollector()

    try:
        if config:
            settings = Settings.from_yaml(Path(config))
        else:
            settings = Settings(
                project_id=project_id,
                project_name=project_name,
                root_path=Path(root_path).resolve(),
                output_dir=Path(output_dir).resolve(),
            )

        PathHelper.ensure_dir(settings.output_dir)
        logger.info("Starting CodeAtlas analysis of %s", settings.root_path)

        # 1. Discover files
        scanner = RepositoryScanner(settings, diagnostics)
        files_by_language = scanner.scan()

        total_files = sum(len(v) for v in files_by_language.values())
        logger.info("Found %d files to analyse", total_files)

        if not total_files:
            click.echo("No source files found. Check your root_path and exclude_patterns.")
            sys.exit(0)

        # 2. Generate artifacts
        artifact_service = ArtifactGenerationService(settings, diagnostics)
        artifacts = artifact_service.generate_all(files_by_language)
        logger.info("Generated %d artifacts", len(artifacts))

        # 3. Build dependency graph
        graph_service = DependencyGraphService(settings, diagnostics)
        graph = graph_service.build(artifacts)

        # 4. Build symbol index
        index_service = SymbolIndexService(settings, diagnostics)
        symbol_index = index_service.build(artifacts)

        # 5. Build manifest
        manifest_service = ManifestGenerationService(settings, diagnostics)
        manifest = manifest_service.build(artifacts)

        # 6. Write graph, index, and manifest
        json_service = JsonSerializationService(settings)
        graph_path = json_service.write_graph(graph)
        index_path = json_service.write_symbol_index(symbol_index)
        manifest_path = json_service.write_manifest(manifest)

        # 7. Report diagnostics
        if diagnostics.has_errors():
            click.echo(DiagnosticsHelper.format_summary(diagnostics), err=True)

        click.echo(
            f"\n✓ CodeAtlas analysis complete\n"
            f"  Artifacts : {len(artifacts)}\n"
            f"  Graph     : {graph_path}\n"
            f"  Index     : {index_path}\n"
            f"  Manifest  : {manifest_path}\n"
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("Fatal error during analysis")
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
