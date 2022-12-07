"""Acceptance test steps for Data Drift service."""

from datetime import datetime, timezone
import json
from typing import Dict
import uuid

from behave import given, then, when
from behave.runner import Context

from raitools.services.data_drift.api.get_record import get_record
from raitools.services.data_drift.api.get_report import get_report

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
    context.record = _get_good_record(context)


@given("a user has an corrupt record")  # type: ignore
def step_given(context: Context) -> None:
    """Adds a good record to the context."""
    context.record = _get_bad_record(context)


@when("they compile the record")  # type: ignore
def step_when(context: Context) -> None:
    """Compiles a record."""
    context.response = _get_response_with_bundle_path(context.bundle_path)
    _write_response_to_disk(context)


@when("they compile the report")  # type: ignore
def step_when(context: Context) -> None:
    """Compiles a report."""
    context.response = get_report(record=context.record)
    _write_response_to_disk(context)


@then("the Data Drift service returns a record in the response")  # type: ignore
def step_then(context: Context) -> None:
    """Takes step."""
    assert context.response["body"]["kind"] == "DataDriftRecord"


@then("the Data Drift service returns a report in the response")  # type: ignore
def step_then(context: Context) -> None:
    """Takes step."""
    assert context.response["body"]["kind"] == "DataDriftReport"
    _write_report_to_disk(context)


@then("the Data Drift service returns an error in the response")  # type: ignore
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


def _get_path_to_bundle_from_spec(spec_filename: str, context: Context) -> str:
    bundle_path = str(prepare_bundle(spec_filename, context.tmp_path))
    return bundle_path


def _get_path_to_well_formed_bundle(context: Context) -> str:
    return _get_path_to_bundle_from_spec("simple_undrifted_spec.json", context)


def _get_path_to_ill_formed_bundle(context: Context) -> str:
    return _get_path_to_bundle_from_spec("bad_simple_undrifted_spec.json", context)


def _get_response_with_bundle_path(bundle_path: str) -> Dict:
    run_timestamp = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
    run_uuid = uuid.uuid4().hex
    response = get_record(
        bundle_path=bundle_path, timestamp=run_timestamp, uuid=run_uuid
    )
    return response


def _get_good_record(context: Context) -> Dict:
    bundle_path = _get_path_to_well_formed_bundle(context)
    response = _get_response_with_bundle_path(bundle_path)
    record = response["body"]
    return record


def _get_bad_record(context: Context) -> Dict:
    record = _get_good_record(context)
    del record["results"]
    return record


def _write_response_to_disk(context: Context) -> None:
    response_path = context.scratch_path / "response.json"
    response_path.write_text(json.dumps(context.response, indent=4))


def _write_report_to_disk(context: Context) -> None:
    response_path = context.scratch_path / "report.html"
    response_path.write_text(context.response["body"]["results"])
