"""Data Drift response."""

from typing import Union

from pydantic import BaseModel

from raitools.rai_error import RaiError
from raitools.services.data_drift.data.data_drift_record import DataDriftRecord
from raitools.services.data_drift.data.data_drift_report import DataDriftReport


class Response(BaseModel):
    """A Data Drift service response."""

    status_code: int
    status_desc: str
    message: str
    body: Union[DataDriftRecord, DataDriftReport, RaiError]
