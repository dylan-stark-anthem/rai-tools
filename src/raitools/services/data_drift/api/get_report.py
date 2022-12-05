"""Data Drift APIs."""

from typing import Dict

from pydantic import ValidationError

from raitools.exceptions import BadRecordError, DataDriftError
from raitools.services.data_drift.api.common import make_error_response, make_response
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord
from raitools.services.data_drift.use_cases.create_report import create_report


def get_report(record: Dict) -> Dict:
    """Gets report from record.

    This is the integration point with components, RESTful APIs, CLIs, etc.
    """
    try:
        result = create_report(
            record=DataDriftRecord(**record), report_builder="plotly"
        )
        return make_response(result).dict()
    except ValidationError as excinfo:
        return make_error_response(
            "Failed to create DataDriftReport.", BadRecordError(*excinfo.args)
        ).dict()
    except DataDriftError as excinfo:
        return make_error_response("Failed to create DataDriftReport.", excinfo).dict()
