"""Tests for feature mappings."""

from typing import Any, Dict
from pydantic import ValidationError
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


@pytest.mark.parametrize(
    "bad_importance_score,expected_error",
    [
        (
            -0.1,
            {
                "ctx": {"limit_value": 0.0},
                "loc": ("importance_score",),
                "msg": "ensure this value is greater than or equal to 0.0",
                "type": "value_error.number.not_ge",
            },
        ),
        (
            1.1,
            {
                "ctx": {"limit_value": 1.0},
                "loc": ("importance_score",),
                "msg": "ensure this value is less than or equal to 1.0",
                "type": "value_error.number.not_le",
            },
        ),
        (
            "forty-two",
            {
                "loc": ("importance_score",),
                "msg": "value is not a valid float",
                "type": "type_error.float",
            },
        ),
        (
            True,
            {
                "loc": ("importance_score",),
                "msg": "value is not a valid float",
                "type": "type_error.float",
            },
        ),
        (
            None,
            {
                "loc": ("importance_score",),
                "msg": "none is not an allowed value",
                "type": "type_error.none.not_allowed",
            },
        ),
    ],
)
def test_feature_importance_score_not_valid(
    bad_importance_score: Any,
    expected_error: Dict,
) -> None:
    """Tests that we raise error if rank not valid."""
    with pytest.raises(ValidationError) as excinfo:
        Feature(
            name="some_name", kind="numerical", importance_score=bad_importance_score
        )

    assert expected_error in excinfo.value.errors()
