"""Tests for response data model."""

from typing import Dict
import pytest

from pydantic import ValidationError

from raitools.rai_error import RaiError
from raitools.services.data_drift.data.response import Response


@pytest.fixture
def fields() -> Dict:
    """Fields for response."""
    return dict(
        status_code=42,
        status_desc="Some desc",
        message="Some message",
        body=RaiError(message="Some error"),
    )


@pytest.mark.parametrize(
    "field_name", [("status_code"), ("status_desc"), ("message"), ("body")]
)
def test_error_if_missing_required_fields(field_name: str, fields: Dict) -> None:
    """Tests we raise error if required field is missing."""
    with pytest.raises(ValidationError) as excinfo:
        del fields[field_name]
        Response(**fields)

    assert {
        "loc": (field_name,),
        "msg": "field required",
        "type": "value_error.missing",
    } in excinfo.value.errors()
