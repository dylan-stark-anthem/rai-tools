"""Tests for process bundle use case."""

from typing import Dict

from raitools.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.data_drift.use_cases.process_bundle import (
    ProcessBundleRequest,
    process_bundle,
)


def test_can_process_bundle(
    simple_request: ProcessBundleRequest, simple_record: DataDriftRecord
) -> None:
    """Tests that we can process a bundle."""
    record = process_bundle(simple_request)

    _assert_equal_dicts(simple_record.dict(), record.dict())


def _assert_equal_dicts(expected_dict: Dict, actual_dict: Dict) -> None:
    """Asserts that two dictionaries have the same members.

    This is a bit nicer than just `==`ing the dictionaries because any
    assertion error is thrown at the spot that it occurs.
    """
    for key in expected_dict:
        assert key in actual_dict
        if isinstance(expected_dict[key], dict):
            _assert_equal_dicts(expected_dict[key], actual_dict[key])
        else:
            assert expected_dict[key] == actual_dict[key]
