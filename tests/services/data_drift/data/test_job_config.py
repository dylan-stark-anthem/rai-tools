"""Tests for data drift job config."""

from typing import Dict
from pydantic import ValidationError
import pytest

from raitools.exceptions import BadJobConfigError
from raitools.services.data_drift.data.job_config import DataDriftJobConfig


@pytest.fixture
def full_job_config_dict() -> Dict:
    """A full job config."""
    job_config = {
        "service_name": "data_drift",
        "report_name": "Some report name",
        "dataset_name": "Some dataset name",
        "dataset_version": "v0.1.0",
        "feature_mapping_filename": "feature_mapping.csv",
        "baseline_data_filename": "baseline_data.csv",
        "test_data_filename": "test_data.csv",
        "model_catalog_id": "123",
    }
    return job_config


@pytest.mark.parametrize(
    "field_name",
    [
        ("service_name"),
        ("report_name"),
        ("dataset_name"),
        ("dataset_version"),
        ("feature_mapping_filename"),
        ("baseline_data_filename"),
        ("test_data_filename"),
        ("model_catalog_id"),
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
    "service_name,error",
    [
        (
            "",
            BadJobConfigError(
                'Service name must be "data_drift"; user-provided "" is not valid'
            ),
        ),
        (
            "not_data_drift",
            BadJobConfigError(
                'Service name must be "data_drift"; user-provided "not_data_drift" is not valid'
            ),
        ),
    ],
)
def test_error_on_invalid_service_name(
    service_name: str, error: BadJobConfigError, full_job_config_dict: Dict
) -> None:
    """Tests that we raise error if service name is invalid."""
    full_job_config_dict["service_name"] = service_name

    with pytest.raises(BadJobConfigError) as excinfo:
        DataDriftJobConfig(**full_job_config_dict)

    assert type(excinfo.value) == type(error) and excinfo.value.args == error.args


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
