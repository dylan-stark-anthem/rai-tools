"""Tests for feature mappings."""

import pytest

from raitools.services.data_drift.domain.feature_mapping import Feature, FeatureMapping
from raitools.services.data_drift.exceptions import BadFeatureMappingError


def test_unsupported_kind() -> None:
    """Tests that we raise error if kind is not supported."""
    actual_kind = "some_unsupported_kind"
    expected_error = BadFeatureMappingError(
        f"Feature kind '{actual_kind}' is not supported. "
        "Supported feature kinds are 'numerical' and 'categorical."
    )

    with pytest.raises(expected_error.__class__) as excinfo:
        Feature(name="some_feature_name", kind=actual_kind, importance_score=0.123)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


def test_empty_feature_mapping() -> None:
    """Tests that we raise error if feature mapping is empty."""
    expected_error = BadFeatureMappingError("Feature mapping is empty.")

    with pytest.raises(expected_error.__class__) as excinfo:
        FeatureMapping(feature_mapping={})

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )
