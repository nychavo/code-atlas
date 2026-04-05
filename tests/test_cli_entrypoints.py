"""Tests for CLI entrypoints and output-directory defaults."""

from pathlib import Path
from typing import cast

from click import Command
from click.testing import CliRunner

from codeatlas.app import project_selector, runner
from codeatlas.config.settings import Settings


class TestRunnerCli:
    def test_defaults_output_dir_to_root_atlas(self, tmp_path: Path, monkeypatch) -> None:
        project_root = tmp_path / "demo_project"
        project_root.mkdir()
        captured: dict[str, object] = {}

        def _fake_execute(settings, verbose: bool = False) -> int:
            captured["settings"] = settings
            captured["verbose"] = verbose
            return 0

        monkeypatch.setattr(runner, "execute_with_settings", _fake_execute)

        result = CliRunner().invoke(cast(Command, runner.main), [str(project_root)])

        assert result.exit_code == 0
        settings = cast(Settings, captured["settings"])
        assert settings.root_path == project_root.resolve()
        assert settings.output_dir == project_root.resolve() / "atlas"

    def test_honors_explicit_output_dir(self, tmp_path: Path, monkeypatch) -> None:
        project_root = tmp_path / "demo_project"
        output_dir = tmp_path / "custom_output"
        project_root.mkdir()
        captured: dict[str, object] = {}

        def _fake_execute(settings, verbose: bool = False) -> int:
            captured["settings"] = settings
            return 0

        monkeypatch.setattr(runner, "execute_with_settings", _fake_execute)

        result = CliRunner().invoke(
            cast(Command, runner.main), [str(project_root), "-o", str(output_dir)]
        )

        assert result.exit_code == 0
        settings = cast(Settings, captured["settings"])
        assert settings.output_dir == output_dir.resolve()


class TestProjectSelectorCli:
    def test_selects_project_and_defaults_output_dir(self, tmp_path: Path, monkeypatch) -> None:
        project_root = tmp_path / "selected_project"
        project_root.mkdir()
        captured: dict[str, object] = {}

        monkeypatch.setattr(
            project_selector,
            "PROJECTS",
            {
                "demo": {
                    "root_path": str(project_root),
                    "project_id": "demo_id",
                    "project_name": "Demo",
                }
            },
        )

        def _fake_execute(settings, verbose: bool = False) -> int:
            captured["settings"] = settings
            return 0

        monkeypatch.setattr(project_selector.runner, "execute_with_settings", _fake_execute)

        result = CliRunner().invoke(cast(Command, project_selector.main), input="demo\n")

        assert result.exit_code == 0
        settings = cast(Settings, captured["settings"])
        assert settings.project_id == "demo_id"
        assert settings.root_path == project_root.resolve()
        assert settings.output_dir == project_root.resolve() / "atlas"

    def test_selector_honors_explicit_output_dir(self, tmp_path: Path, monkeypatch) -> None:
        project_root = tmp_path / "selected_project"
        output_dir = tmp_path / "atlas_output"
        project_root.mkdir()
        captured: dict[str, object] = {}

        monkeypatch.setattr(
            project_selector,
            "PROJECTS",
            {
                "demo": {
                    "root_path": str(project_root),
                    "project_id": "demo_id",
                    "project_name": "Demo",
                }
            },
        )

        def _fake_execute(settings, verbose: bool = False) -> int:
            captured["settings"] = settings
            return 0

        monkeypatch.setattr(project_selector.runner, "execute_with_settings", _fake_execute)

        result = CliRunner().invoke(
            cast(Command, project_selector.main),
            ["-o", str(output_dir)],
            input="demo\n",
        )

        assert result.exit_code == 0
        settings = cast(Settings, captured["settings"])
        assert settings.output_dir == output_dir.resolve()

