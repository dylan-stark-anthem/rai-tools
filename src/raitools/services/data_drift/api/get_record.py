"""Data Drift APIs."""

from pathlib import Path
from typing import Dict

from raitools.services.data_drift.bundles import create_bundle_from_zip
from raitools.exceptions import DataDriftError
from raitools.services.data_drift.api.common import make_error_response, make_response
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
        return make_response(record).dict()
    except DataDriftError as excinfo:
        return make_error_response("Failed to create DataDriftRecord.", excinfo).dict()
