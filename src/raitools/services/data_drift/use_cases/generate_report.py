"""HTML report generation."""

from typing import Any, Callable
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord

from raitools.services.data_drift.domain.data_drift_report import DataDriftReportRecord


def generate_report(
    record: DataDriftRecord,
    report_record: DataDriftReportRecord,
    report_builder: Callable[[DataDriftRecord, DataDriftReportRecord], Any],
) -> Any:
    """Generates a report for the given record."""
    report = report_builder(record, report_record)
    return report
