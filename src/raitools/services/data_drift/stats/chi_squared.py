"""Chi-Squared statistical test.

This implementation bridges the concrete stat implementation into the data
drift service. It knows both the specific interface for the concrete
implementation and the general interface that the data drift service will
work with.
"""

from typing import List

from raitools import stats
from raitools.services.data_drift.stats.common import StatisticalTestResultType


def chi_squared(baseline_data: List, test_data: List) -> StatisticalTestResultType:
    """Applies Chi-Squared test."""
    test_statistic, p_value = stats.chi_squared(baseline_data, test_data)

    return StatisticalTestResultType(
        test_statistic=test_statistic,
        p_value=p_value,
    )
