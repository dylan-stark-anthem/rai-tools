"""The data drift record."""

from pathlib import Path
from pydantic import BaseModel

from raitools.data_drift.domain.job_config import JobConfig


class BundleManifestMetadata(BaseModel):
    """Bundle manifest metadata."""

    bundle_path: Path
    job_config_filename: str
    data_filename: str


class BundleManifest(BaseModel):
    """A bundle manifest."""

    metadata: BundleManifestMetadata
    job_config: JobConfig


class DataDriftRecord(BaseModel):
    """A Data Drift record."""

    bundle_manifest: BundleManifest
