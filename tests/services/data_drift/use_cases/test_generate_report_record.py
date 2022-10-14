"""Tests generating data drift report record."""

import pytest

from raitools.services.data_drift.use_cases.generate_report_record import (
    generate_report_record,
)

from tests.asserts import assert_equal_records
from tests.services.data_drift.use_cases.common import (
    prepare_record,
    prepare_report_record,
)


@pytest.mark.parametrize(
    "record_filename,report_record_filename",
    [
        ("simple_undrifted_record.json", "simple_undrifted_report_record.json"),
        ("simple_drifted_record.json", "simple_drifted_report_record.json"),
        ("no_numerical_record.json", "no_numerical_report_record.json"),
        ("no_categorical_record.json", "no_categorical_report_record.json"),
    ],
)
def test_can_generate_report_record(
    record_filename: str, report_record_filename: str
) -> None:
    """Tests that we can generate a report record."""
    simple_undrifted_record = prepare_record(record_filename)

    actual_report_record = generate_report_record(simple_undrifted_record)

    expected_report_record = prepare_report_record(report_record_filename)
    assert_equal_records(expected_report_record, actual_report_record)
