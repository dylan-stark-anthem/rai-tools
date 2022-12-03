"""Tests for generate report use case."""

import bs4
import pytest

from raitools.services.data_drift.use_cases.generate_report import generate_report

from tests.services.data_drift.use_cases.common import prepare_record, prepare_report


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
def test_can_generate_report(
    record_filename: str,
    report_html_filename: str,
) -> None:
    """Tests that we can generate an HTML report."""
    record = prepare_record(record_filename)
    expected_report_html = prepare_report(report_html_filename)

    report = generate_report(
        record,
        report_builder="simple",
    )
    actual_report_html = report.results

    _assert_equal_htmls(expected_report_html, actual_report_html)


def _assert_equal_htmls(expected_html: str, actual_html: str) -> None:
    """Asserts two HTMLs are equal.

    The goal here is to not impose restrictions on the expected HTML that
    we save under resources/ or the actual HTML we generate. Instead, we
    enforce consistent formatting here, so that they are comparable.
    """

    def strip_extra_space(string: str) -> str:
        string = string.replace("\n", "")
        string = string.replace(
            '" ,', '",'
        )  # because VSCODE keeps adding spaces when updating
        string = string.replace(
            '" .', '".'
        )  # because VSCODE keeps adding spaces when updating
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
