"""Process data drift bundle."""

from pathlib import Path

import pyarrow as pa
from pydantic import BaseModel

from raitools.data_drift.domain.bundle import create_bundle_from_zip
from raitools.data_drift.domain.data_drift_record import (
    BundleManifest,
    BundleManifestMetadata,
    DataDriftRecord,
)
from raitools.data_drift.domain.data_summary import DataSummary


class Request(BaseModel):
    """A process bundle request."""

    bundle_path: Path


def create_data_summary(data: pa.Table) -> DataSummary:
    """Creates summary statistics for a dataset."""
    return DataSummary(
        num_rows=data.num_rows,
        num_columns=data.num_columns,
    )


def process_bundle(request: Request) -> DataDriftRecord:
    """Processes a data drift bundle."""
    bundle = create_bundle_from_zip(request.bundle_path)
    baseline_data_summary = create_data_summary(bundle.baseline_data)
    test_data_summary = create_data_summary(bundle.test_data)

    record = DataDriftRecord(
        bundle_manifest=BundleManifest(
            metadata=BundleManifestMetadata(
                bundle_path=request.bundle_path,
                job_config_filename=bundle.job_config_filename,
                baseline_data_filename=bundle.baseline_data_filename,
                test_data_filename=bundle.test_data_filename,
            ),
            job_config=bundle.job_config,
            baseline_data_summary=baseline_data_summary,
            test_data_summary=test_data_summary,
        )
    )

    return record
