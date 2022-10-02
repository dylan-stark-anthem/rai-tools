"""The data drift record."""

from pathlib import Path
from typing import List
from pydantic import BaseModel
from raitools.data_drift.domain.data_summary import DataSummary

from raitools.data_drift.domain.job_config import JobConfig
from raitools.data_drift.domain.data_drift_summary import DataDriftDataSummary
from raitools.data_drift.domain.statistical_test import StatisticalTest


class BundleManifestMetadata(BaseModel):
    """Bundle manifest metadata."""

    bundle_path: Path
    job_config_filename: str
    baseline_data_filename: str
    test_data_filename: str


class BundleManifest(BaseModel):
    """A bundle manifest."""

    metadata: BundleManifestMetadata
    job_config: JobConfig
    baseline_data_summary: DataSummary
    test_data_summary: DataSummary


class DataDriftRecord(BaseModel):
    """A Data Drift record."""

    bundle_manifest: BundleManifest
    data_summary: DataDriftDataSummary
    statistical_tests: List[StatisticalTest]
