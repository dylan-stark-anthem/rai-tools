"""Common API methods."""


from typing import Any

from raitools.exceptions import DataDriftError
from raitools.rai_error import RaiError
from raitools.services.data_drift.data.response import Response


def make_response(result: Any) -> Response:
    """Makes an API response."""
    return Response(
        status_code=200,
        status_desc="Success",
        message=f"{result.__repr_name__()} was retrieved successfully",
        body=result,
    )


def make_error_response(message: str, error: DataDriftError) -> Response:
    """Makes an API error response."""
    return Response(
        status_code=error.code,
        status_desc="Failure",
        message=message,
        body=RaiError(message=str(error)),
    )
