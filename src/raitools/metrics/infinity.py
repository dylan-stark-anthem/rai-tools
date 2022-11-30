"""infinity distance metrics.

This implementation does not depend on anything inside a service. It only
depends on concrete implementations from external packages.
"""

from typing import List

from scipy.spatial import distance


def infinity(baseline_data: List, test_data: List) -> float:
    """Applies infinity distance."""
    infinity_distance = distance.chebyshev(baseline_data, test_data)
    return infinity_distance
