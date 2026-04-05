"""Diagnostic formatting and reporting helpers."""

from pathlib import Path

from codeatlas.core.diagnostics import DiagnosticRecord, DiagnosticsCollector
from codeatlas.utils.json_helper import JsonHelper


class DiagnosticsHelper:
    """Static helpers for formatting and persisting diagnostic records."""

    @staticmethod
    def format_diagnostic(record: DiagnosticRecord) -> str:
        """Return a single-line human-readable representation of *record*."""
        location = ""
        if record.file_path:
            location = record.file_path
            if record.line is not None:
                location += f":{record.line}"
                if record.column is not None:
                    location += f":{record.column}"
            location = f" [{location}]"
        code_part = f" ({record.code})" if record.code else ""
        return f"[{record.severity.upper()}]{location}{code_part} {record.message}"

    @staticmethod
    def format_summary(collector: DiagnosticsCollector) -> str:
        """Return a multi-line summary of all diagnostics in *collector*."""
        records = collector.get_all()
        if not records:
            return "No diagnostics."
        lines = [DiagnosticsHelper.format_diagnostic(r) for r in records]
        summary = collector.to_dict()
        lines.append(
            f"\nTotal: {summary['total']} "
            f"(errors: {summary['errors']}, warnings: {summary['warnings']})"
        )
        return "\n".join(lines)

    @staticmethod
    def write_diagnostics_report(collector: DiagnosticsCollector, path: Path) -> None:
        """Write all diagnostics from *collector* to a JSON file at *path*."""
        JsonHelper.write_dict(collector.to_dict(), path)
