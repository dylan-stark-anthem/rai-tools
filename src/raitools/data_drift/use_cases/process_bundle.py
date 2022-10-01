"""Process data drift bundle."""

from pathlib import Path
from pydantic import BaseModel

from raitools.data_drift.domain.data_drift_record import (
    BundleManifest,
    BundleManifestMetadata,
    DataDriftRecord,
)


class Request(BaseModel):
    """A process bundle request."""

    bundle_path: Path


def process_bundle(request: Request) -> DataDriftRecord:
    """Processes a data drift bundle."""
    record = DataDriftRecord(
        manifest=BundleManifest(
            metadata=BundleManifestMetadata(bundle_path=request.bundle_path)
        )
    )

    return record
