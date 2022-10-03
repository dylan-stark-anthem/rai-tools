"""Statistical tests for data drift."""

from typing import Callable, Dict, TypedDict

from raitools.data_drift.domain.stats.chi_squared import chi_squared
from raitools.data_drift.domain.stats.kolmogorov_smirnov import kolmogorov_smirnov


class StatisticalTest(TypedDict):
    """Statistical test."""

    name: str
    kind: str
    method: Callable


statistical_tests: Dict[str, Dict[str, StatisticalTest]] = {
    "numerical": {
        "kolmogorov-smirnov": {
            "name": "kolmogorov-smirnov",
            "kind": "numerical",
            "method": kolmogorov_smirnov,
        }
    },
    "categorical": {
        "chi-squared": {
            "name": "chi-squared",
            "kind": "categorical",
            "method": chi_squared,
        }
    },
}
