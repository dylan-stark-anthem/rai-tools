"""Data Drift APIs."""

from pathlib import Path
from typing import Any, Dict

from pydantic import ValidationError

from raitools.services.data_drift.domain.bundle import create_bundle_from_zip
from raitools.rai_error import RaiError
from raitools.exceptions import BadRecordError, DataDriftError
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.domain.response import Response
from raitools.services.data_drift.use_cases.create_report import create_report
from raitools.services.data_drift.use_cases.create_record import (
    create_record_from_bundle,
)


def get_record(bundle_path: str, timestamp: str, uuid: str) -> Dict:
    """Gets record.

    This is the integration point with components, RESTful APIs, CLIs, etc.
    """
    try:
        bundle = create_bundle_from_zip(Path(bundle_path))
        record = create_record_from_bundle(
            bundle=bundle,
            bundle_filename=Path(bundle_path).name,
            timestamp=timestamp,
            uuid=uuid,
        )
        return _make_response(record).dict()
    except DataDriftError as excinfo:
        return _make_error_response("Failed to create DataDriftRecord.", excinfo).dict()


def get_report(record: Dict) -> Dict:
    """Gets report from record.

    This is the integration point with components, RESTful APIs, CLIs, etc.
    """
    try:
        result = create_report(
            record=DataDriftRecord(**record), report_builder="plotly"
        )
        return _make_response(result).dict()
    except ValidationError as excinfo:
        return _make_error_response(
            "Failed to create DataDriftReport.", BadRecordError(*excinfo.args)
        ).dict()
    except DataDriftError as excinfo:
        return _make_error_response("Failed to create DataDriftReport.", excinfo).dict()


def _make_response(result: Any) -> Response:
    return Response(
        status_code=200,
        status_desc="Success",
        message=f"{result.__repr_name__()} was retrieved successfully",
        body=result,
    )


def _make_error_response(message: str, error: DataDriftError) -> Response:
    return Response(
        status_code=error.code,
        status_desc="Failure",
        message=message,
        body=RaiError(message=str(error)),
    )
