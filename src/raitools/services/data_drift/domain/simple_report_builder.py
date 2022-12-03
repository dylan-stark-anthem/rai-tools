"""Simple report builder."""


from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.domain.html_report_builder import (
    HtmlReportBuilder,
    basic_data_summary_maker,
    basic_drift_magnitude_maker,
    basic_drift_summary_maker,
)


def simple_report_builder(record: DataDriftRecord) -> str:
    """Creates a report builder for the simple test case."""
    report_builder = HtmlReportBuilder()
    report_builder.data_summary_maker = basic_data_summary_maker
    report_builder.drift_summary_maker = basic_drift_summary_maker
    report_builder.drift_magnitude_maker = basic_drift_magnitude_maker
    report_builder.record = record
    report_builder.compile()
    return report_builder.get()
