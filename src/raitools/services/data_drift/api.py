"""Data Drift APIs."""

from pathlib import Path
from typing import Any, Dict
from raitools.domain.rai_error import RaiError
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.domain.response import Response
from raitools.services.data_drift.use_cases.generate_report import generate_report

from raitools.services.data_drift.use_cases.process_bundle import process_bundle


def get_record(bundle_path: str, timestamp: str, uuid: str) -> Dict:
    """Gets record.

    This is the integration point with KFP, FastAPI, CLI, etc.
    """
    result = process_bundle(
        bundle_path=Path(bundle_path),
        timestamp=timestamp,
        uuid=uuid,
    )
    response = _construct_response(result)
    return response.dict()


def get_report(record: Dict) -> Dict:
    """Gets report from record.

    This is the integration point with KFP, FastAPI, CLI, etc.
    """
    report_builder = "plotly"
    result = generate_report(
        record=DataDriftRecord(**record), report_builder=report_builder
    )
    response = _construct_response(result)
    return response.dict()


def _construct_response(result: Any) -> Response:
    if isinstance(result, RaiError):
        return Response(
            status_code=result.code,
            status_desc=result.description,
            message=result.message,
            body=result,
        )

    return Response(
        status_code=200,
        status_desc="Success",
        message=f"{result.__repr_name__()} was retrieved successfully",
        body=result,
    )
