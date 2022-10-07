"""Chi-Squared statistical test."""

from typing import List

import numpy as np
from scipy.stats.contingency import chi2_contingency

from raitools.services.data_drift.domain.statistical_test_result import (
    StatisticalTestResult,
)


class ChiSquaredTestResult(StatisticalTestResult):
    """Results for Chi-Squared statistical test."""

    dof: int
    expected: np.ndarray

    class Config:
        """Configuration."""

        arbitrary_types_allowed = True


def chi_squared(baseline_data: List, test_data: List) -> StatisticalTestResult:
    """Applies Chi-Squared test."""
    observed = _create_contingency_table(baseline_data, test_data)
    chi2, p, dof, expected = chi2_contingency(observed)

    return ChiSquaredTestResult(
        statistic=chi2,
        p_value=p,
        dof=dof,
        expected=expected,
    )


def _create_contingency_table(baseline_data: List, test_data: List) -> List[List[int]]:
    """Creates a contingency table."""
    categories = set(baseline_data).union(set(test_data))
    baseline_counts = {category: 0 for category in categories}
    for value in baseline_data:
        baseline_counts[value] += 1
    test_counts = {category: 0 for category in categories}
    for value in test_data:
        test_counts[value] += 1
    observed = [
        [baseline_counts[category] for category in categories],
        [test_counts[category] for category in categories],
    ]

    return observed
