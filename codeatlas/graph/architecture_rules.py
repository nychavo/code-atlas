"""Architecture rule checker — validates layer dependency constraints."""

from codeatlas.config.settings import Settings
from codeatlas.models.graph_models import DependencyEdge


class ViolationRecord:
    """Describes a single architecture rule violation."""

    def __init__(
        self,
        source_layer: str,
        target_layer: str,
        source_artifact: str,
        target_module: str,
        rule: str,
    ) -> None:
        self.source_layer = source_layer
        self.target_layer = target_layer
        self.source_artifact = source_artifact
        self.target_module = target_module
        self.rule = rule

    def to_dict(self) -> dict:
        """Serialise the record to a plain dictionary."""
        return {
            "source_layer": self.source_layer,
            "target_layer": self.target_layer,
            "source_artifact": self.source_artifact,
            "target_module": self.target_module,
            "rule": self.rule,
        }


class ArchitectureRules:
    """Checks dependency edges against configured architecture layer rules."""

    def __init__(self, settings: Settings, layer_map: dict[str, str]) -> None:
        """Initialise with settings and a mapping of artifact_id → layer name."""
        self.settings = settings
        self.layer_map = layer_map

    def check(self, edges: list[DependencyEdge]) -> list[ViolationRecord]:
        """Return violations found in *edges* according to configured rules."""
        violations: list[ViolationRecord] = []
        rules = self.settings.architecture_rules

        if not rules:
            return violations

        for edge in edges:
            source_layer = self.layer_map.get(edge.source_artifact, "unknown")
            target_layer = self.layer_map.get(edge.target_artifact or "", "unknown")

            for rule in rules:
                if rule.source_layer != source_layer:
                    continue
                if target_layer in rule.forbidden_targets:
                    violations.append(
                        ViolationRecord(
                            source_layer=source_layer,
                            target_layer=target_layer,
                            source_artifact=edge.source_artifact,
                            target_module=edge.target_module,
                            rule=f"{source_layer} must not depend on {target_layer}",
                        )
                    )

        return violations
