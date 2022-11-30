"""jensen_shannon distance metrics.

This implementation does not depend on anything inside a service. It only
depends on concrete implementations from external packages.
"""

from typing import List

from scipy.spatial import distance


def jensen_shannon(baseline_data: List, test_data: List) -> float:
    """Applies infinity distance."""
    jensen_shannon_distance = distance.jensenshannon(baseline_data, test_data)
    return jensen_shannon_distance
