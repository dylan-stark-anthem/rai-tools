"""Kilmogorov-Smirnov statistical test."""

from typing import List

from raitools.services.data_drift.domain.statistical_test_result import (
    StatisticalTestResult,
)
from raitools import stats


def kolmogorov_smirnov(baseline_data: List, test_data: List) -> StatisticalTestResult:
    """Applies Kilmogorov-Smirnov test."""
    test_statistic, p_value = stats.kolmogorov_smirnov(baseline_data, test_data)

    return StatisticalTestResult(
        test_statistic=test_statistic,
        p_value=p_value,
    )
