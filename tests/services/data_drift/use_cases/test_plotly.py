"""Plotly tests."""

from pathlib import Path

import pytest

from raitools.services.data_drift.use_cases.create_report import create_report
from tests.services.data_drift.use_cases.common import prepare_record


@pytest.mark.parametrize(
    "record_filename,report_html_filename",
    [
        (
            "simple_undrifted_record.json",
            "simple_undrifted_report.html",
        ),
        (
            "simple_drifted_record.json",
            "simple_drifted_report.html",
        ),
        (
            "no_numerical_record.json",
            "no_numerical_report.html",
        ),
        (
            "no_categorical_record.json",
            "no_categorical_report.html",
        ),
        (
            "with_113_features_record.json",
            "with_113_features_report.html",
        ),
        (
            "with_13_features_record.json",
            "with_13_features_report.html",
        ),
    ],
)
def test_can_generate_report_with_plotly(
    record_filename: str, report_html_filename: str
) -> None:
    """Tests that we can generate a report with Plotly.

    The test only ensures that we can generate report HTML without error.

    Note: All HTML files are writen out under `scratch/` for easier manual review.
    """
    output_path = Path("scratch/tests/services/data_drift/helpers/test_plotly")
    record = prepare_record(record_filename)

    report = create_report(record, report_builder="plotly")

    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / report_html_filename
    report_path.write_text(report.results)
