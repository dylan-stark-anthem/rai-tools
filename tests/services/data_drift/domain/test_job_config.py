"""Tests for data drift job config."""

from typing import Dict
from pydantic import ValidationError
import pytest

from raitools.services.data_drift.domain.job_config import DataDriftJobConfig


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
