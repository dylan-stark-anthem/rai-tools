"""HTML report generation."""

from pathlib import Path

from pydantic import BaseModel

from raitools.data_drift.domain.data_drift_record import DataDriftRecord


class DataDriftReport(BaseModel):
    """A data drift report."""


def generate_report(record: DataDriftRecord, output_path: Path) -> None:
    """Generates a report for the given record."""
    report_name = record.bundle.job_config.report_name
    report_filename = f"{report_name}.html"
    report_path = output_path / report_filename
    report_path.write_text("{}")
