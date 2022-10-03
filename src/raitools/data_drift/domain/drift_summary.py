"""Drift summary."""


from pydantic import BaseModel

from raitools.data_drift.domain.statistical_test_result import StatisticalTestResult


class DriftSummary(BaseModel):
    """Drift summary."""

    name: str
    result: StatisticalTestResult


class FeatureSummary(BaseModel):
    """Feature summary."""

    name: str
    kind: str
    statistical_test: DriftSummary
