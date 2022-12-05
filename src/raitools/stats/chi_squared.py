"""Chi-Squared statistical test.

This implementation does not depend on anything inside a service. It only
depends on concrete implementations from external packages.
"""


from typing import List, Tuple

from scipy.stats.contingency import chi2_contingency


def chi_squared(baseline_data: List, test_data: List) -> Tuple[float, float]:
    """Applies Chi-Squared test."""
    observed = create_contingency_table(baseline_data, test_data)
    chi2, p, _, _ = chi2_contingency(observed)
    return chi2, p


def create_contingency_table(baseline_data: List, test_data: List) -> List[List[int]]:
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
