"""Acceptance test steps for Data Drift service."""

from datetime import datetime, timezone
from typing import Dict
import uuid

from behave import given, then, when
from behave.runner import Context

from raitools.services.data_drift.api import get_record, get_report

from tests.services.data_drift.use_cases.common import prepare_bundle


@given("a user has a well-formed bundle")  # type: ignore
def step_given(context: Context) -> None:
    """Adds a path to a good bundle to the context."""
    context.bundle_path = _get_path_to_well_formed_bundle(context)


@given("a user has an ill-formed bundle")  # type: ignore
def step_given(context: Context) -> None:
    """Adds a path to a bad bundle to the context."""
    context.bundle_path = _get_path_to_ill_formed_bundle(context)


@given("a user has a record")  # type: ignore
def step_given(context: Context) -> None:
    """Adds a good record to the context."""
    bundle_path = _get_path_to_well_formed_bundle(context)
    response = _get_response_with_bundle_path(bundle_path)
    context.record = response["body"]


@when("they compile the record")  # type: ignore
def step_when(context: Context) -> None:
    """Compiles a record."""
    context.response = _get_response_with_bundle_path(context.bundle_path)


@when("they compile the report")  # type: ignore
def step_when(context: Context) -> None:
    """Compiles a report."""
    context.response = get_report(record=context.record)


@then("the Data Drift service returns a record in the response")  # type: ignore
def step_then(context: Context) -> None:
    """Takes step."""
    assert context.response["body"]["kind"] == "DataDriftRecord"


@then("the Data Drift service returns a report in the response")  # type: ignore
def step_then(context: Context) -> None:
    """Takes step."""
    assert context.response["body"]["kind"] == "DataDriftReport"


@then("the Data Drift services returns an error in the response")  # type: ignore
def step_then(context: Context) -> None:
    """Takes step."""
    response = context.response
    assert response["body"]["kind"] == "RaiError"


@then('the status code is "{expected_status_code:d}"')  # type: ignore
def step_then(context: Context, expected_status_code: int) -> None:
    """Takes step."""
    assert context.response["status_code"] == expected_status_code


@then('the status description is "{expected_status_desc}"')  # type: ignore
def step_then(context: Context, expected_status_desc: str) -> None:
    """Takes step."""
    response = context.response
    assert response["status_desc"] == expected_status_desc


@then('the message is "{expected_status_message}"')  # type: ignore
def step_then(context: Context, expected_status_message: str) -> None:
    """Takes step."""
    response = context.response
    assert response["message"] == expected_status_message


def _get_path_to_well_formed_bundle(context: Context) -> str:
    spec_filename = "simple_undrifted_spec.json"
    bundle_path = str(prepare_bundle(spec_filename, context.tmp_path))
    return bundle_path


def _get_path_to_ill_formed_bundle(context: Context) -> str:
    spec_filename = "bad_simple_undrifted_spec.json"
    bundle_path = str(prepare_bundle(spec_filename, context.tmp_path))
    return bundle_path


def _get_response_with_bundle_path(bundle_path: str) -> Dict:
    """Gets the response for the given bundle."""
    run_timestamp = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    run_uuid = uuid.uuid4().hex
    response = get_record(
        bundle_path=bundle_path, timestamp=run_timestamp, uuid=run_uuid
    )
    return response
