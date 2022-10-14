"""Tests for generate report use case."""


from typing import Callable

import bs4
import pytest

from raitools.services.data_drift.domain.data_drift_report import DataDriftReportRecord
from raitools.services.data_drift.domain.html_report_builder import (
    HtmlReportBuilder,
    basic_data_summary_maker,
    basic_drift_magnitude_maker,
    basic_drift_summary_maker,
)
from raitools.services.data_drift.use_cases.generate_report import generate_report

from tests.services.data_drift.use_cases.common import (
    prepare_report,
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
    ],
)
def test_can_generate_report(
    report_record_filename: str,
    report_html_filename: str,
    simple_undrifted_report_builder: Callable[[DataDriftReportRecord], str],
) -> None:
    """Tests that we can generate an HTML report."""
    simple_undrifted_report_record = prepare_report_record(report_record_filename)

    actual_report_html = generate_report(
        simple_undrifted_report_record,
        report_builder=simple_undrifted_report_builder,
    )

    expected_report_html = prepare_report(report_html_filename)
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


def simple_undrifted_report_builder_impl(report_data: DataDriftReportRecord) -> str:
    """Creates a report builder for the simple test case."""
    report_builder = HtmlReportBuilder()
    report_builder.timestamp = "1970-01-01 00:00:00"
    report_builder.data_summary_maker = basic_data_summary_maker
    report_builder.drift_summary_maker = basic_drift_summary_maker
    report_builder.drift_magnitude_maker = basic_drift_magnitude_maker
    report_builder.report_data = report_data
    report_builder.compile()
    return report_builder.get()


@pytest.fixture
def simple_undrifted_report_builder() -> Callable[[DataDriftReportRecord], str]:
    """Returms simple report builder method."""
    return simple_undrifted_report_builder_impl
