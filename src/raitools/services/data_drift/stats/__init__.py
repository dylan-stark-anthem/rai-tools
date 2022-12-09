"""Statistical tests for data drift."""

from typing import Dict

from raitools.services.data_drift.stats.chi_squared import chi_squared
from raitools.services.data_drift.stats.common import StatisticalTestType
from raitools.services.data_drift.stats.kolmogorov_smirnov import (
    kolmogorov_smirnov,
)


statistical_tests: Dict[str, StatisticalTestType] = {
    "numerical": {
        "name": "kolmogorov-smirnov",
        "kind": "numerical",
        "method": kolmogorov_smirnov,
    },
    "categorical": {
        "name": "chi-squared",
        "kind": "categorical",
        "method": chi_squared,
    },
}
