"""Plotly-based report builder."""

from typing import Any
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord

from raitools.services.data_drift.domain.data_drift_report import DataDriftReportRecord
from raitools.services.data_drift.domain.html_report_builder import HtmlReportBuilder
from raitools.services.data_drift.helpers.plotly import (
    plotly_data_summary_maker,
    plotly_drift_magnitude_maker,
    plotly_drift_summary_maker,
)


def plotly_report_builder(
    record: DataDriftRecord, report_data: DataDriftReportRecord
) -> Any:
    """Builds an HTML report with fancy plotly diagrams."""
    report_builder = HtmlReportBuilder()
    report_builder.data_summary_maker = plotly_data_summary_maker
    report_builder.drift_summary_maker = plotly_drift_summary_maker
    report_builder.drift_magnitude_maker = plotly_drift_magnitude_maker
    report_builder.record = record
    report_builder.report_data = report_data
    report_builder.compile()
    return report_builder.get()
