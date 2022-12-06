"""Kilmogorov-Smirnov statistical test."""

from typing import List

from raitools import stats
from raitools.services.data_drift.data.data_drift_record import StatisticalTestResult


def kolmogorov_smirnov(baseline_data: List, test_data: List) -> StatisticalTestResult:
    """Applies Kilmogorov-Smirnov test."""
    test_statistic, p_value = stats.kolmogorov_smirnov(baseline_data, test_data)

    return StatisticalTestResult(
        test_statistic=test_statistic,
        p_value=p_value,
    )
