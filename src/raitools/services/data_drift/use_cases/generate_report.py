"""HTML report generation."""

from typing import Any, Callable

from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord


def generate_report(
    record: DataDriftRecord,
    report_builder: Callable[[DataDriftRecord], Any],
) -> Any:
    """Generates a report for the given record."""
    report = report_builder(record)
    return report
