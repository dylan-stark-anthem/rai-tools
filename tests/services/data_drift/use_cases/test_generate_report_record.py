"""Tests generating data drift report record."""

from raitools.services.data_drift.use_cases.generate_report_record import (
    generate_report_record,
)

from tests.asserts import assert_equal_records
from tests.services.data_drift.use_cases.common import (
    prepare_record,
    prepare_report_record,
)


def test_can_generate_report_record() -> None:
    """Tests that we can generate a report record."""
    simple_undrifted_record = prepare_record("simple_undrifted_record.json")

    actual_report_record = generate_report_record(simple_undrifted_record)

    expected_report_record = prepare_report_record(
        "simple_undrifted_report_record.json"
    )
    assert_equal_records(expected_report_record, actual_report_record)
