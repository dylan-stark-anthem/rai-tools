"""Process data drift bundle."""

from pathlib import Path
from pydantic import BaseModel

from raitools.data_drift.domain.bundle import create_bundle_from_zip
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
    bundle = create_bundle_from_zip(request.bundle_path)

    record = DataDriftRecord(
        bundle_manifest=BundleManifest(
            metadata=BundleManifestMetadata(
                bundle_path=request.bundle_path,
                job_config_filename=bundle.job_config_filename,
                data_filename=bundle.data_filename,
            ),
            job_config=bundle.job_config,
        )
    )

    return record
