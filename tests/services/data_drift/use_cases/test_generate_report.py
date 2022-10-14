"""Tests for generate report use case."""


from typing import Callable

import bs4

from raitools.services.data_drift.domain.data_drift_report import DataDriftReportData
from raitools.services.data_drift.use_cases.generate_report import generate_report

from tests.services.data_drift.use_cases.fixtures.common import (
    prepare_record,
    prepare_report,
)


def test_can_generate_report(
    simple_undrifted_report_builder: Callable[[DataDriftReportData], str]
) -> None:
    """Tests that we can generate an HTML report."""
    simple_undrifted_record = prepare_record("simple_undrifted_record.json")

    actual_report_html = generate_report(
        simple_undrifted_record,
        report_builder=simple_undrifted_report_builder,
    )

    expected_report_html = prepare_report("simple_undrifted_report.html")
    _assert_equal_htmls(expected_report_html, actual_report_html)


def _assert_equal_htmls(expected_html: str, actual_html: str) -> None:
    """Asserts two HTMLs are equal.

    The goal here is to not impose restrictions on the expected HTML that
    we save under resources/ or the actual HTML we generate. Instead, we
    enforce consistent formatting here, so that they are comparable.
    """

    def strip_extra_space(string: str) -> str:
        string = string.replace("\n", "")
        tokens = string.split()
        return " ".join(tokens)

    formatter = bs4.formatter.HTMLFormatter(strip_extra_space)

    expected_html = expected_html.strip()
    expected_soup = bs4.BeautifulSoup(expected_html, "html.parser")

    actual_html = actual_html.strip()
    actual_report_soup = bs4.BeautifulSoup(actual_html, "html.parser")

    assert expected_soup.prettify(formatter=formatter) == actual_report_soup.prettify(
        formatter=formatter
    )
