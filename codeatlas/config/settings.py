"""Application configuration models."""

from pathlib import Path

from pydantic import BaseModel


class ArchitectureLayerRule(BaseModel):
    """A rule constraining allowed inter-layer dependencies."""

    source_layer: str
    allowed_targets: list[str]
    forbidden_targets: list[str]


class LayerPattern(BaseModel):
    """Maps file-path glob patterns to an architectural layer name."""

    layer: str
    patterns: list[str]


class AnalyzerConfig(BaseModel):
    """Configuration for individual language analyzers."""

    use_jedi: bool = True
    use_astroid: bool = True
    use_grimp: bool = True
    use_pyan: bool = False
    max_file_size_bytes: int = 1_000_000


_DEFAULT_LAYER_PATTERNS: list[LayerPattern] = [
    LayerPattern(layer="api", patterns=["**/api/**", "**/routes/**", "**/views/**", "**/endpoints/**"]),
    LayerPattern(layer="service", patterns=["**/services/**", "**/service/**"]),
    LayerPattern(layer="repository", patterns=["**/repositories/**", "**/repos/**", "**/dao/**"]),
    LayerPattern(layer="model", patterns=["**/models/**", "**/model/**", "**/entities/**"]),
    LayerPattern(layer="core", patterns=["**/core/**"]),
    LayerPattern(layer="utils", patterns=["**/utils/**", "**/helpers/**", "**/util/**"]),
    LayerPattern(layer="config", patterns=["**/config/**", "**/settings/**", "**/conf/**"]),
    LayerPattern(layer="test", patterns=["**/tests/**", "**/test_*.py", "**/*_test.py"]),
]


class Settings(BaseModel):
    """Global settings for a CodeAtlas analysis run."""

    project_id: str = "default"
    project_name: str = "Unknown Project"
    root_path: Path
    output_dir: Path
    include_patterns: list[str] = ["**/*.py"]
    exclude_patterns: list[str] = [
        "**/node_modules/**",
        "**/.git/**",
        "**/__pycache__/**",
        "**/dist/**",
        "**/build/**",
        "**/.venv/**",
        "**/venv/**",
        "**/*.egg-info/**",
    ]
    supported_languages: list[str] = ["python"]
    schema_version: str = "1.0.0"
    analyzer_config: AnalyzerConfig = AnalyzerConfig()
    layer_patterns: list[LayerPattern] = _DEFAULT_LAYER_PATTERNS
    architecture_rules: list[ArchitectureLayerRule] = []
    log_level: str = "INFO"

    @classmethod
    def from_yaml(cls, path: Path) -> "Settings":
        """Load settings from a YAML file at *path*."""
        import yaml

        with open(path) as fh:
            data = yaml.safe_load(fh)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Construct Settings from a plain dictionary."""
        return cls(**data)
