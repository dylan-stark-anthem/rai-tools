"""Data Drift APIs."""

from pathlib import Path
from typing import Any, Dict
from raitools.domain.rai_error import RaiError

from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.domain.response import Response
from raitools.services.data_drift.exceptions import DataDriftError
from raitools.services.data_drift.use_cases.generate_report import generate_report
from raitools.services.data_drift.use_cases.process_bundle import process_bundle


def get_record(bundle_path: str, timestamp: str, uuid: str) -> Dict:
    """Gets record.

    This is the integration point with components, RESTful APIs, CLIs, etc.
    """
    try:
        result = process_bundle(
            bundle_path=Path(bundle_path),
            timestamp=timestamp,
            uuid=uuid,
        )
        return _make_response(result).dict()
    except DataDriftError as excinfo:
        return _make_error_response("Failed to create DataDriftRecord.", excinfo).dict()


def get_report(record: Dict) -> Dict:
    """Gets report from record.

    This is the integration point with components, RESTful APIs, CLIs, etc.
    """
    try:
        result = generate_report(
            record=DataDriftRecord(**record), report_builder="plotly"
        )
        return _make_response(result).dict()
    except DataDriftError as excinfo:
        return _make_error_response("Faised to create DataDriftReport.", excinfo).dict()


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
