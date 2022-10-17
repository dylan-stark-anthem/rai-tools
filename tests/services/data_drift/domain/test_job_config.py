"""Tests for data drift job config."""

from typing import Any, Dict
from pydantic import ValidationError
import pytest

from raitools.services.data_drift.domain.job_config import DataDriftJobConfig
from raitools.services.data_drift.exceptions import BadJobConfigError


@pytest.fixture
def full_job_config_dict() -> Dict:
    """A full job config."""
    job_config = {
        "report_name": "Some report name",
        "dataset_name": "Some dataset name",
        "dataset_version": "v0.1.0",
        "baseline_data_filename": "baseline_data.csv",
        "test_data_filename": "test_data.csv",
        "model_catalog_id": "123",
        "feature_mapping": {
            "numerical_feature_0": {
                "name": "numerical_feature_0",
                "kind": "numerical",
                "rank": 1,
            }
        },
    }
    return job_config


@pytest.mark.parametrize(
    "field_name",
    [
        ("report_name"),
        ("dataset_name"),
        ("dataset_version"),
        ("baseline_data_filename"),
        ("test_data_filename"),
        ("model_catalog_id"),
        ("feature_mapping"),
    ],
)
def test_job_config_without_field(field_name: str, full_job_config_dict: Dict) -> None:
    """Tests that we raise error if required field not provided."""
    del full_job_config_dict[field_name]

    with pytest.raises(ValidationError) as excinfo:
        DataDriftJobConfig(**full_job_config_dict)
    assert {
        "loc": (field_name,),
        "msg": "field required",
        "type": "value_error.missing",
    } in excinfo.value.errors()


@pytest.mark.parametrize(
    "field_name",
    [
        ("name"),
        ("rank"),
        ("kind"),
    ],
)
def test_job_config_feature_without_field(
    field_name: str, full_job_config_dict: Dict
) -> None:
    """Tests that we raise error if required field not provided."""
    del full_job_config_dict["feature_mapping"]["numerical_feature_0"][field_name]

    with pytest.raises(ValidationError) as excinfo:
        DataDriftJobConfig(**full_job_config_dict)
    assert {
        "loc": (
            "feature_mapping",
            "numerical_feature_0",
            field_name,
        ),
        "msg": "field required",
        "type": "value_error.missing",
    } in excinfo.value.errors()


@pytest.mark.parametrize(
    "report_name,error",
    [
        ("", BadJobConfigError("Report name is empty.")),
        (".", BadJobConfigError("Report name '.' does not start with `[a-zA-Z]`.")),
        ("_", BadJobConfigError("Report name '_' does not start with `[a-zA-Z]`.")),
        ("*", BadJobConfigError("Report name '*' does not start with `[a-zA-Z]`.")),
        (" ", BadJobConfigError("Report name ' ' does not start with `[a-zA-Z]`.")),
        ("a*", BadJobConfigError("Report name 'a*' contains unsupported characters.")),
        (
            "abc, DEF, and 123",
            BadJobConfigError(
                "Report name 'abc, DEF, and 123' contains unsupported characters."
            ),
        ),
        ("a ", BadJobConfigError("Report name 'a ' ends with a space.")),
    ],
)
def test_report_name_with_special_characters(
    report_name: str, error: BadJobConfigError, full_job_config_dict: Dict
) -> None:
    """Tests that we raise error if report name has unsupported characters."""
    full_job_config_dict["report_name"] = report_name

    with pytest.raises(BadJobConfigError) as excinfo:
        DataDriftJobConfig(**full_job_config_dict)

    assert type(excinfo.value) == type(error) and excinfo.value.args == error.args


@pytest.mark.parametrize(
    "bad_mapping",
    [
        (42),
        (4.2),
        ("forty-two"),
        (True),
    ],
)
def test_feature_mapping_is_a_simple_value(
    bad_mapping: Any, full_job_config_dict: Dict
) -> None:
    """Tests that we raise error if feature mapping is a simple value."""
    full_job_config_dict["feature_mapping"] = bad_mapping

    with pytest.raises(ValidationError) as excinfo:
        DataDriftJobConfig(**full_job_config_dict)

    assert {
        "loc": ("feature_mapping",),
        "msg": "value is not a valid dict",
        "type": "type_error.dict",
    } in excinfo.value.errors()


def test_feature_mapping_is_a_list_of_features(full_job_config_dict: Dict) -> None:
    """Tests that we raise error if feature mapping is a list of features."""
    bad_mapping = [{"name": "name", "kind": "kind", "rank": 1}]
    full_job_config_dict["feature_mapping"] = bad_mapping

    with pytest.raises(ValidationError) as excinfo:
        DataDriftJobConfig(**full_job_config_dict)

    assert {
        "loc": ("feature_mapping",),
        "msg": "value is not a valid dict",
        "type": "type_error.dict",
    } in excinfo.value.errors()


@pytest.mark.parametrize("bad_mapping", [({}), ([])])
def test_feature_mapping_is_empty(bad_mapping: str, full_job_config_dict: Dict) -> None:
    """Tests that we raise error if feature mapping is empty."""
    expected_error = BadJobConfigError("Feature mapping is empty.")
    full_job_config_dict["feature_mapping"] = bad_mapping

    with pytest.raises(BadJobConfigError) as excinfo:
        DataDriftJobConfig(**full_job_config_dict)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )


def test_feature_mapping_key_not_in_feature(full_job_config_dict: Dict) -> None:
    """Tests that we raise error if feature mapping key not in associated value."""
    feature_mapping_key = "numerical_feature_0"
    feature_name = "not_numerical_feature_0"
    expected_error = BadJobConfigError(
        f"Feature mapping key '{feature_mapping_key}' does not match feature name '{feature_name}'"
    )
    full_job_config_dict["feature_mapping"][feature_mapping_key]["name"] = feature_name

    with pytest.raises(BadJobConfigError) as excinfo:
        DataDriftJobConfig(**full_job_config_dict)

    assert (
        type(excinfo.value) == type(expected_error)
        and excinfo.value.args == expected_error.args
    )
