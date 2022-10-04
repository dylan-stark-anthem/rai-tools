"""Tests for generate report use case."""


from pathlib import Path

import pytest

from raitools.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.data_drift.use_cases.generate_report import (
    DataDriftReport,
    generate_report,
)


def test_can_generate_report(
    simple_record: DataDriftRecord, simple_report: DataDriftReport, tmp_path: Path
) -> None:
    """Tests that we can generate an HTML report."""
    report = generate_report(simple_record, output_path=tmp_path)

    assert report == simple_report


@pytest.fixture
def simple_report() -> DataDriftReport:
    """The expected report for the simple record."""
    return DataDriftReport()
