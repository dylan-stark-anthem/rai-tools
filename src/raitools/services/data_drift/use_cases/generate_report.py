"""Data Drift report generation."""

from typing import Any, Callable

from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.domain.data_drift_report import DataDriftReport
from raitools.services.data_drift.domain.plotly_report_builder import (
    plotly_report_builder,
)
from raitools.services.data_drift.domain.simple_report_builder import (
    simple_report_builder,
)


def generate_report(record: DataDriftRecord, report_builder: str) -> DataDriftReport:
    """Generates a report for the given record."""
    report_builder_impl = _get_report_builder(report_builder)
    report = DataDriftReport(results=report_builder_impl(record))
    return report


def _get_report_builder(name: str) -> Callable[[DataDriftRecord], Any]:
    """Gets report builder implementation by name."""
    REPORT_BUILDERS = {
        "simple": simple_report_builder,
        "plotly": plotly_report_builder,
    }
    return REPORT_BUILDERS[name]
