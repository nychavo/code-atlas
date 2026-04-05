"""Confidence scoring helpers."""


class ConfidenceHelper:
    """Static helpers for assigning confidence scores to analysis results."""

    DEFAULT_HIGH: float = 0.95
    DEFAULT_MEDIUM: float = 0.6
    DEFAULT_LOW: float = 0.3

    @staticmethod
    def score_import(is_resolved: bool, is_stdlib: bool) -> float:
        """Score the confidence of an import record.

        Standard-library imports that are resolved receive the highest
        confidence; unresolved third-party imports receive medium confidence.
        """
        if is_stdlib:
            return ConfidenceHelper.DEFAULT_HIGH
        if is_resolved:
            return ConfidenceHelper.DEFAULT_HIGH
        return ConfidenceHelper.DEFAULT_MEDIUM

    @staticmethod
    def score_call_target(is_resolved: bool, is_same_file: bool) -> float:
        """Score the confidence of a call-target reference."""
        if is_resolved and is_same_file:
            return ConfidenceHelper.DEFAULT_HIGH
        if is_resolved:
            return ConfidenceHelper.DEFAULT_MEDIUM
        return ConfidenceHelper.DEFAULT_LOW

    @staticmethod
    def score_base_class(is_resolved: bool) -> float:
        """Score the confidence of a base-class reference."""
        if is_resolved:
            return ConfidenceHelper.DEFAULT_HIGH
        return ConfidenceHelper.DEFAULT_MEDIUM
