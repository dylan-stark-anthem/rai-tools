"""Tests for create record use case."""

from pathlib import Path

import pytest

from raitools.services.data_drift.bundles import create_bundle_from_zip
from raitools.services.data_drift.use_cases.create_record import (
    create_record_from_bundle,
)

from tests.asserts import assert_equal_records
from tests.services.data_drift.use_cases.common import prepare_bundle, prepare_record


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
def test_can_process_bundle(
    spec_filename: str, record_filename: str, tmp_path: Path
) -> None:
    """Tests that we can process a bundle."""
    bundle_path = prepare_bundle(spec_filename, tmp_path)
    bundle = create_bundle_from_zip(bundle_path)
    expected_record = prepare_record(record_filename)

    actual_record = create_record_from_bundle(
        bundle=bundle,
        bundle_filename=bundle_path.name,
        timestamp=expected_record.results.metadata.timestamp,
        uuid=expected_record.results.metadata.uuid,
    )

    assert_equal_records(expected_record, actual_record)
