"""Plotly tests."""

from pathlib import Path

import pytest

from raitools.services.data_drift.domain.plotly_report_builder import (
    plotly_report_builder,
)
from raitools.services.data_drift.use_cases.generate_report import generate_report
from tests.services.data_drift.use_cases.common import (
    prepare_report_record,
)


@pytest.mark.parametrize(
    "report_record_filename,report_html_filename",
    [
        ("simple_undrifted_report_record.json", "simple_undrifted_report.html"),
        ("simple_drifted_report_record.json", "simple_drifted_report.html"),
        ("no_numerical_report_record.json", "no_numerical_report.html"),
        ("no_categorical_report_record.json", "no_categorical_report.html"),
        ("with_113_features_report_record.json", "with_113_features_report.html"),
        ("with_13_features_report_record.json", "with_13_features_report.html"),
    ],
)
def test_can_generate_report_with_plotly(
    report_record_filename: str,
    report_html_filename: str,
) -> None:
    """Tests that we can generate a report with Plotly.

    The test only ensures that we can generate report HTML without error.

    Note: All HTML files are writen out under `scratch/` for easier manual review.
    """
    output_path = Path("scratch/tests/services/data_drift/helpers/test_plotly")
    report_record = prepare_report_record(report_record_filename)

    report_html = generate_report(report_record, report_builder=plotly_report_builder)

    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / report_html_filename
    report_path.write_text(report_html)
