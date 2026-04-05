"""Interactive CLI entry point for selecting and scanning known projects."""

from pathlib import Path

import click

from codeatlas.app import runner
from codeatlas.config.settings import Settings

# Add more projects here as needed.
PROJECTS: dict[str, dict[str, str]] = {
    "code-atlas": {
        "root_path": r"C:\_mystuff\_mywork\python\code-atlas",
        "project_id": "code_atlas",
        "project_name": "Code Atlas",
    }
}


def _prompt_project_key() -> str:
    """Prompt user to pick one of the configured project keys."""
    click.echo("Available projects:")
    for key, metadata in PROJECTS.items():
        click.echo(f"- {key}: {metadata['root_path']}")

    return click.prompt(
        "Enter project key",
        type=click.Choice(sorted(PROJECTS.keys()), case_sensitive=False),
    )


@click.command()
@click.option(
    "--output-dir",
    "-o",
    default=None,
    type=click.Path(),
    help="Output directory (defaults to <selected_project_root>/atlas)",
)
@click.option("--verbose", "-v", is_flag=True, default=False, help="Enable verbose logging")
def main(output_dir: str | None, verbose: bool) -> None:
    """Select a configured project and run CodeAtlas analysis."""
    selected_key = _prompt_project_key()
    selected = PROJECTS[selected_key]

    root_path = Path(selected["root_path"]).resolve()
    resolved_output = Path(output_dir).resolve() if output_dir else root_path / "atlas"

    settings = Settings(
        project_id=selected["project_id"],
        project_name=selected["project_name"],
        root_path=root_path,
        output_dir=resolved_output,
    )

    exit_code = runner.execute_with_settings(settings, verbose)
    if exit_code:
        raise SystemExit(exit_code)

