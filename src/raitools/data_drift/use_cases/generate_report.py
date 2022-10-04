"""HTML report generation."""

from pathlib import Path

from pydantic import BaseModel

from raitools.data_drift.domain.data_drift_record import DataDriftRecord


class DataDriftReport(BaseModel):
    """A data drift report."""


def generate_report(record: DataDriftRecord, output_path: Path) -> DataDriftReport:
    """Generates a report for the given record."""
    return DataDriftReport()
