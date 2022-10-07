"""Tests for generate report use case."""


from pathlib import Path

import bs4

from raitools.data_drift.domain.data_drift_record import (
    DataDriftRecord,
)
from raitools.data_drift.domain.html_report_builder import HtmlReportBuilder
from raitools.data_drift.use_cases.generate_report import generate_report


def test_can_generate_report(
    simple_record: DataDriftRecord,
    simple_report_builder: HtmlReportBuilder,
    simple_report_html: str,
    tmp_path: Path,
) -> None:
    """Tests that we can generate an HTML report."""
    generate_report(
        simple_record,
        output_path=tmp_path,
        report_builder=simple_report_builder,
    )

    actual_report_filename = f"{simple_record.bundle.job_config.report_name}.html"
    actual_report_path = tmp_path / actual_report_filename
    actual_report_html = actual_report_path.read_text()
    actual_report_soup = bs4.BeautifulSoup(actual_report_html, "html.parser")
    expected_soup = bs4.BeautifulSoup(simple_report_html, "html.parser")
    assert expected_soup.prettify() == actual_report_soup.prettify()
