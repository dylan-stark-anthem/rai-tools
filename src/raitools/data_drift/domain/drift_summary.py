"""Drift summary."""


from pydantic import BaseModel

from raitools.data_drift.domain.statistical_test_result import StatisticalTestResult


class DriftSummary(BaseModel):
    """Drift summary."""

    name: str
    result: StatisticalTestResult
    significance_level: float
    adjusted_significance_level: float
    outcome: str


class Feature(BaseModel):
    """Feature."""

    name: str
    kind: str
    rank: int


class FeatureSummary(BaseModel):
    """Feature summary."""

    name: str
    kind: str
    rank: int
    statistical_test: DriftSummary
    drift_status: str
