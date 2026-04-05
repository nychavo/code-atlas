"""Diagnostics collection for CodeAtlas analysis runs."""

import threading
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from codeatlas.core.enums import DiagnosticSeverity


class DiagnosticRecord(BaseModel):
    """A single diagnostic message produced during analysis."""

    severity: str
    message: str
    file_path: str | None = None
    line: int | None = None
    column: int | None = None
    code: str | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DiagnosticsCollector:
    """Thread-safe collector for diagnostic records produced during analysis."""

    def __init__(self) -> None:
        self._records: list[DiagnosticRecord] = []
        self._lock = threading.Lock()

    def add_error(
        self,
        message: str,
        *,
        file_path: str | None = None,
        line: int | None = None,
        column: int | None = None,
        code: str | None = None,
    ) -> None:
        """Record an error-level diagnostic."""
        self._add(DiagnosticSeverity.ERROR, message, file_path=file_path, line=line, column=column, code=code)

    def add_warning(
        self,
        message: str,
        *,
        file_path: str | None = None,
        line: int | None = None,
        column: int | None = None,
        code: str | None = None,
    ) -> None:
        """Record a warning-level diagnostic."""
        self._add(DiagnosticSeverity.WARNING, message, file_path=file_path, line=line, column=column, code=code)

    def add_info(
        self,
        message: str,
        *,
        file_path: str | None = None,
        line: int | None = None,
        column: int | None = None,
        code: str | None = None,
    ) -> None:
        """Record an info-level diagnostic."""
        self._add(DiagnosticSeverity.INFO, message, file_path=file_path, line=line, column=column, code=code)

    def _add(
        self,
        severity: DiagnosticSeverity,
        message: str,
        *,
        file_path: str | None,
        line: int | None,
        column: int | None,
        code: str | None,
    ) -> None:
        record = DiagnosticRecord(
            severity=severity.value,
            message=message,
            file_path=file_path,
            line=line,
            column=column,
            code=code,
        )
        with self._lock:
            self._records.append(record)

    def get_all(self) -> list[DiagnosticRecord]:
        """Return all collected diagnostic records."""
        with self._lock:
            return list(self._records)

    def get_errors(self) -> list[DiagnosticRecord]:
        """Return only error-level records."""
        with self._lock:
            return [r for r in self._records if r.severity == DiagnosticSeverity.ERROR.value]

    def get_warnings(self) -> list[DiagnosticRecord]:
        """Return only warning-level records."""
        with self._lock:
            return [r for r in self._records if r.severity == DiagnosticSeverity.WARNING.value]

    def has_errors(self) -> bool:
        """Return True if any error-level records have been collected."""
        with self._lock:
            return any(r.severity == DiagnosticSeverity.ERROR.value for r in self._records)

    def clear(self) -> None:
        """Remove all collected records."""
        with self._lock:
            self._records.clear()

    def to_dict(self) -> dict[str, Any]:
        """Serialise all records to a plain dictionary."""
        with self._lock:
            return {
                "total": len(self._records),
                "errors": sum(1 for r in self._records if r.severity == DiagnosticSeverity.ERROR.value),
                "warnings": sum(1 for r in self._records if r.severity == DiagnosticSeverity.WARNING.value),
                "records": [r.model_dump() for r in self._records],
            }
