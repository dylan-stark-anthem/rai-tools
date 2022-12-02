"""Acceptance test steps for Data Drift service."""

from datetime import datetime, timezone
from typing import Any
import uuid

from behave import given, then, when
from behave.runner import Context

from raitools.services.data_drift.domain.request import Request
from raitools.services.data_drift.domain.response import Response
from raitools.services.data_drift.use_cases.process_bundle import process_bundle

from tests.services.data_drift.use_cases.common import prepare_bundle

@given("a user has a well-formed bundle")
def given_well_formed_bundle(context: Context) -> None:
    """Adds a path to a good bundle to the context."""
    spec_filename = "simple_undrifted_spec.json"
    context.bundle_path = prepare_bundle(spec_filename, context.tmp_path)


@when("they compile the record")
def when_they_compile_record(context: Context) -> None:
    """Compiles a record."""
    run_timestamp = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    run_uuid = uuid.uuid4().hex
    request = create_record_request(bundle_path=context.bundle_path, timestamp=run_timestamp, uuid=run_uuid)
    context.response = get_record(request)


@then("the Data Drift service returns success")
def then_we_return_success(context: Context) -> None:
    """Takes step."""
    assert context.response.status_code == 200
    assert context.response.status_desc == "Success"
    assert context.response.message == "Record retrieved successfully."


def create_record_request(**kwargs: Any) -> Request:
    """Creates a record request."""
    return Request(**kwargs)


def get_record(request: Request) -> Response:
    """Gets record."""
    response = process_bundle(
        request.bundle_path,
        timestamp=request.timestamp,
        uuid=request.uuid,
    )

    if response.kind == "DataDriftRecord":
        return Response(
            status_code=200,
            status_desc="Success",
            message="Record retrieved successfully.",
            response=response,
        )
    elif response.kind == "RaiError":
        return Response(
            status_code=response.code,
            status_desc=response.description,
            message=response.message,
            response=response
        )
    else:
        raise NotImplementedError(f"Received unexpected response of kind '{response.kind}'")
