"""Tests for generate report use case."""


from typing import Callable

import bs4

from raitools.services.data_drift.domain.data_drift_record import (
    DataDriftRecord,
)
from raitools.services.data_drift.domain.data_drift_report import DataDriftReportData
from raitools.services.data_drift.use_cases.generate_report import generate_report


def test_can_generate_report(
    simple_undrifted_record: DataDriftRecord,
    simple_undrifted_report_builder: Callable[[DataDriftReportData], str],
    simple_undrifted_report_html: str,
) -> None:
    """Tests that we can generate an HTML report."""
    actual_report_html = generate_report(
        simple_undrifted_record,
        report_builder=simple_undrifted_report_builder,
    )

    actual_report_soup = bs4.BeautifulSoup(actual_report_html, "html.parser")
    expected_soup = bs4.BeautifulSoup(simple_undrifted_report_html, "html.parser")
    assert expected_soup.prettify() == actual_report_soup.prettify()
