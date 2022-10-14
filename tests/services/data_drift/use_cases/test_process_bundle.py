"""Tests for process bundle use case."""

from pathlib import Path
from typing import Dict

import pytest

from raitools.services.data_drift.use_cases.process_bundle import process_bundle

from tests.services.data_drift.use_cases.fixtures.common import (
    prepare_bundle,
    prepare_record,
)


@pytest.mark.parametrize(
    "spec_filename,record_filename",
    [
        ("simple_undrifted_spec.json", "simple_undrifted_record.json"),
        ("simple_drifted_spec.json", "simple_drifted_record.json"),
    ],
)
def test_can_process_simple_drifted_bundle(
    spec_filename: str, record_filename: str, tmp_path: Path
) -> None:
    """Tests that we can process a bundle."""
    bundle_path = prepare_bundle(spec_filename, tmp_path)

    record = process_bundle(bundle_path)

    expected_record = prepare_record(record_filename)
    _assert_equal_dicts(expected_record.dict(), record.dict())


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
