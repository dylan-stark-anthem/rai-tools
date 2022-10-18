"""The data drift record."""

from typing import Dict

from pydantic import BaseModel, Field

import raitools
from raitools.services.data_drift.domain.job_config import DataDriftJobConfig
from raitools.services.data_drift.domain.statistical_test_result import (
    StatisticalTestResult,
)
from raitools.services.data_drift.domain.types import (
    DriftStatus,
    FeatureKind,
    FeatureName,
    FileName,
    Name,
    NonNegativeCount,
    PositiveCount,
    Probability,
    StatisticalTestOutcome,
)


class BundleManifest(BaseModel):
    """A bundle manifest."""

    bundle_filename: FileName
    job_config_filename: FileName
    baseline_data_filename: FileName
    test_data_filename: FileName


class BundleData(BaseModel):
    """Bundle data."""

    filename: FileName
    num_rows: PositiveCount
    num_columns: PositiveCount


class RecordBundle(BaseModel):
    """A bundle."""

    job_config: DataDriftJobConfig
    data: Dict[str, BundleData]
    manifest: BundleManifest


class RecordMetadata(BaseModel):
    """Metadata for data drift record."""

    raitools_version: str = Field(raitools.__version__, const=True)


class DriftSummaryMetadata(BaseModel):
    """Summary statistics for data."""

    num_numerical_features: NonNegativeCount
    num_categorical_features: NonNegativeCount


class FeatureStatisticalTest(BaseModel):
    """Drift summary."""

    name: Name
    result: StatisticalTestResult
    significance_level: Probability
    adjusted_significance_level: Probability
    outcome: StatisticalTestOutcome


class DriftSummaryFeature(BaseModel):
    """Feature summary."""

    name: FeatureName
    kind: FeatureKind
    rank: PositiveCount
    statistical_test: FeatureStatisticalTest
    drift_status: DriftStatus


class RecordDriftSummary(BaseModel):
    """Data drift record drift summary."""

    features: Dict[str, DriftSummaryFeature]
    metadata: DriftSummaryMetadata


class DataDriftRecord(BaseModel):
    """A Data Drift record."""

    apiVersion: str = Field("raitools/v1", const=True)
    kind: str = Field("DataDriftRecord", const=True)
    metadata: RecordMetadata
    bundle: RecordBundle
    drift_summary: RecordDriftSummary
