"""Chi-Squared statistical test.

This implementation does not depend on anything inside a service. It only
depends on concrete implementations from external packages.
"""

from typing import List

from scipy.stats import ks_2samp

from raitools.stats.types import StatisticalTestResultType


def kolmogorov_smirnov(
    baseline_data: List, test_data: List
) -> StatisticalTestResultType:
    """Applies Kilmogorov-Smirnov test."""
    statistic, pvalue = ks_2samp(baseline_data, test_data, method="asymp")
    return statistic, pvalue
