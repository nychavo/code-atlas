"""Abstract base class for summary generators."""

from abc import ABC, abstractmethod
from typing import Any

from codeatlas.models.artifact_models import SummaryRecord


class BaseSummaryGenerator(ABC):
    """Abstract base for generators that produce SummaryRecord objects."""

    @abstractmethod
    def generate_summary(self, artifact_data: dict[str, Any], settings: Any) -> SummaryRecord:
        """Generate and return a SummaryRecord from *artifact_data*."""
        ...
