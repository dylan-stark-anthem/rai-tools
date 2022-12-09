"""Kilmogorov-Smirnov statistical test."""

from typing import List

from raitools import stats
from raitools.services.data_drift.stats.common import StatisticalTestResultType


def kolmogorov_smirnov(
    baseline_data: List, test_data: List
) -> StatisticalTestResultType:
    """Applies Kilmogorov-Smirnov test."""
    test_statistic, p_value = stats.kolmogorov_smirnov(baseline_data, test_data)

    return StatisticalTestResultType(
        test_statistic=test_statistic,
        p_value=p_value,
    )
