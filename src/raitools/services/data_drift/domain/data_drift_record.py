"""The data drift record."""

from pathlib import Path
from typing import Dict

from pydantic import BaseModel

from raitools.services.data_drift.domain.job_config import DataDriftJobConfig
from raitools.services.data_drift.domain.statistical_test_result import (
    StatisticalTestResult,
)


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


class RecordBundle(BaseModel):
    """A bundle."""

    job_config: DataDriftJobConfig
    data: Dict[str, BundleData]
    manifest: BundleManifest


class RecordMetadata(BaseModel):
    """Metadata for data drift record."""

    raitools_version: str


class DriftSummaryMetadata(BaseModel):
    """Summary statistics for data."""

    num_numerical_features: int
    num_categorical_features: int


class FeatureStatisticalTest(BaseModel):
    """Drift summary."""

    name: str
    result: StatisticalTestResult
    significance_level: float
    adjusted_significance_level: float
    outcome: str


class DriftSummaryFeature(BaseModel):
    """Feature summary."""

    name: str
    kind: str
    rank: int
    statistical_test: FeatureStatisticalTest
    drift_status: str


class RecordDriftSummary(BaseModel):
    """Data drift record drift summary."""

    features: Dict[str, DriftSummaryFeature]
    metadata: DriftSummaryMetadata


class DataDriftRecord(BaseModel):
    """A Data Drift record."""

    apiVersion: str = "raitools/v1"
    kind: str = "DataDriftRecord"
    metadata: RecordMetadata
    bundle: RecordBundle
    drift_summary: RecordDriftSummary
