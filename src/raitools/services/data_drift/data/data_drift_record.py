"""The data drift record."""

from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConstrainedFloat, ConstrainedInt, Field

import raitools
from raitools.services.data_drift.data.job_config import DataDriftJobConfig
from raitools.services.data_drift.data.common import (
    FileName,
    ImportanceScore,
    Name,
)


class FeatureName(Name):
    """A feature name."""


class FeatureKind(str, Enum):
    """A kind of feature."""

    numerical = "numerical"
    categorical = "categorical"


class PositiveCount(ConstrainedInt):
    """A positive count."""

    ge = 1
    strict = True


class NonNegativeCount(ConstrainedInt):
    """A non-negative count."""

    ge = 0
    strict = True


class Probability(ConstrainedFloat):
    """A probability value in [0, 1]."""

    ge = 0.0
    le = 1.0
    strict = True


class StatisticalTestOutcome(str, Enum):
    """A statistical test outcome."""

    reject_null_hypothesis = "reject null hypothesis"
    fail_to_reject_null_hypothesis = "fail to reject null hypothesis"


class DriftStatus(str, Enum):
    """A drift status."""

    drifted = "drifted"
    not_drifted = "not drifted"


class BundleManifest(BaseModel):
    """A bundle manifest."""

    bundle_filename: FileName
    job_config_filename: FileName
    feature_mapping_filename: FileName
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


class StatisticalTestResult(BaseModel):
    """Results of a statistical test."""

    test_statistic: float
    p_value: float


class FeatureStatisticalTest(BaseModel):
    """Drift summary."""

    name: Name
    result: StatisticalTestResult
    significance_level: Probability
    outcome: StatisticalTestOutcome


class DriftSummaryFeature(BaseModel):
    """Feature summary."""

    name: FeatureName
    kind: FeatureKind
    rank: PositiveCount
    importance_score: ImportanceScore
    statistical_test: FeatureStatisticalTest
    drift_status: DriftStatus


class RecordDataSummary(BaseModel):
    """Data drift record data summary."""

    num_numerical_features: NonNegativeCount
    num_categorical_features: NonNegativeCount


class RecordDriftSummary(BaseModel):
    """Data drift record drift summary."""

    num_total_features: PositiveCount
    num_features_drifted: NonNegativeCount
    top_10_features_drifted: NonNegativeCount
    top_20_features_drifted: NonNegativeCount


class RecordDriftDetails(BaseModel):
    """Data drift record drift details."""

    fields: List[str]
    observations: Dict[str, Any]


class ResultMetadata(BaseModel):
    """Data drift result metadata."""

    report_name: Name
    timestamp: str
    uuid: str
    thresholds: Dict[str, Dict[str, float]]


class RecordResults(BaseModel):
    """Data drift record results."""

    metadata: ResultMetadata
    data_summary: RecordDataSummary
    drift_summary: RecordDriftSummary
    drift_details: RecordDriftDetails
    features: Dict[str, DriftSummaryFeature]


class DataDriftRecord(BaseModel):
    """A Data Drift record."""

    apiVersion: str = Field("raitools/v1", const=True)
    kind: str = Field("DataDriftRecord", const=True)
    metadata: RecordMetadata = RecordMetadata()
    results: RecordResults
    bundle: RecordBundle
