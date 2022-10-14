"""HTML report generation."""

from typing import Any, Callable

from raitools.services.data_drift.domain.data_drift_report import DataDriftReportRecord


def generate_report(
    report_record: DataDriftReportRecord,
    report_builder: Callable[[DataDriftReportRecord], Any],
) -> Any:
    """Generates a report for the given record."""
    report = report_builder(report_record)
    return report
