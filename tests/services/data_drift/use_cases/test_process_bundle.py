"""Tests for process bundle use case."""

from pathlib import Path
from typing import Any

import pytest
from raitools.services.data_drift.exceptions import BadPathToBundleError

from raitools.services.data_drift.use_cases.process_bundle import process_bundle

from tests.asserts import assert_equal_records
from tests.services.data_drift.use_cases.common import (
    prepare_bundle,
    prepare_record,
)


@pytest.mark.parametrize(
    "spec_filename,record_filename",
    [
        ("simple_undrifted_spec.json", "simple_undrifted_record.json"),
        ("simple_drifted_spec.json", "simple_drifted_record.json"),
        ("no_numerical_spec.json", "no_numerical_record.json"),
        ("no_categorical_spec.json", "no_categorical_record.json"),
        ("with_113_features_spec.json", "with_113_features_record.json"),
        ("with_13_features_spec.json", "with_13_features_record.json"),
    ],
)
def test_can_process_simple_drifted_bundle(
    spec_filename: str, record_filename: str, tmp_path: Path
) -> None:
    """Tests that we can process a bundle."""
    bundle_path = prepare_bundle(spec_filename, tmp_path)

    actual_record = process_bundle(bundle_path)

    expected_record = prepare_record(record_filename)
    assert_equal_records(expected_record, actual_record)


@pytest.mark.parametrize(
    "bundle_path,error_message",
    [
        (
            "/some/str/path",
            "Path to bundle is not a valid `pathlib.Path`, it's a(n) `<class 'str'>`.",
        ),
        (
            42,
            "Path to bundle is not a valid `pathlib.Path`, it's a(n) `<class 'int'>`.",
        ),
        (
            4.2,
            "Path to bundle is not a valid `pathlib.Path`, it's a(n) `<class 'float'>`.",
        ),
    ],
)
def test_path_to_bundle_not_a_path(bundle_path: Any, error_message: str) -> None:
    """Tests that we raise appropriate error if path to bundle is not a Path."""
    with pytest.raises(BadPathToBundleError) as excinfo:
        process_bundle(bundle_path)
    assert error_message in str(excinfo.value)
