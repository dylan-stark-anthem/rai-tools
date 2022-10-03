"""The data drift record."""

from pathlib import Path
from typing import Dict

from pydantic import BaseModel
from raitools.data_drift.domain.data_drift_summary import DataDriftDataSummary

from raitools.data_drift.domain.drift_summary import FeatureSummary
from raitools.data_drift.domain.job_config import JobConfig
from raitools.data_drift.domain.statistical_test import StatisticalTest


class BundleManifest(BaseModel):
    """A bundle manifest."""

    bundle_path: Path
    job_config_filename: str
    baseline_data_filename: str
    test_data_filename: str


class BundleData(BaseModel):
    """Bundle data."""

    filename: str
    num_rows: int
    num_columns: int


class Bundle(BaseModel):
    """A bundle."""

    job_config: JobConfig
    data: Dict[str, BundleData]
    manifest: BundleManifest


class DataDriftMetadata(BaseModel):
    """Metadata for data drift record."""

    raitools_version: str


class DataDriftRecordDriftSummary(BaseModel):
    """Data drift record drift summary."""

    features: Dict[str, FeatureSummary]
    metadata: DataDriftDataSummary


class DataDriftRecord(BaseModel):
    """A Data Drift record."""

    apiVersion: str = "raitools/v1"
    kind: str = "DataDriftRecord"
    metadata: DataDriftMetadata
    bundle: Bundle
    statistical_tests: Dict[str, StatisticalTest]
    drift_summary: DataDriftRecordDriftSummary
