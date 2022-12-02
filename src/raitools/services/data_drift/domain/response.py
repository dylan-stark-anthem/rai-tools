"""Data Drift response."""

from typing import Union

from pydantic import BaseModel

from raitools.domain.rai_error import RaiError
from raitools.services.data_drift.domain.data_drift_record import DataDriftRecord


class Response(BaseModel):
    """A Data Drift service response."""

    status_code: int
    status_desc: str
    message: str
    response: Union[DataDriftRecord, RaiError]
