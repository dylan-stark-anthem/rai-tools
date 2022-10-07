"""Kilmogorov-Smirnov statistical test."""

from typing import List

from scipy.stats import ks_2samp

from raitools.services.data_drift.domain.statistical_test_result import (
    StatisticalTestResult,
)


def kolmogorov_smirnov(baseline_data: List, test_data: List) -> StatisticalTestResult:
    """Applies Kilmogorov-Smirnov test."""
    statistic, p_value = ks_2samp(baseline_data, test_data, method="asymp")
    return StatisticalTestResult(
        statistic=statistic,
        p_value=p_value,
    )
