"""Types of data drift."""

from enum import Enum
import re
from pydantic import ConstrainedFloat, ConstrainedInt, ConstrainedStr, StrictStr


class Rank(ConstrainedInt):
    """A rank."""

    ge = 1
    strict = True


class ImportanceScore(ConstrainedFloat):
    """An importance score."""

    ge = 0.0
    le = 1.0
    strict = True


class Name(ConstrainedStr):
    """A report name."""

    min_length = 1
    max_length = 128
    regex = re.compile(r"^[a-zA-Z][a-zA-Z0-9-._ ]*$")
    strict = True


class FileName(Name):
    """A file name."""


class ReportName(Name):
    """A report name."""


class DatasetName(Name):
    """A dataset name."""


class FeatureName(Name):
    """A feature name."""


class FeatureKind(str, Enum):
    """A kind of feature."""

    numerical = "numerical"
    categorical = "categorical"


class DatasetVersion(ConstrainedStr):
    """A dataset version.

    This will match versions like

    - `0`, `0.0`, and `0.0.0`, or
    - `v0`, `v0.0`, and `v0.0.0`
    """

    regex = re.compile(r"^(v)?(0|[1-9]\d*)(.(0|[1-9]\d*)(.(0|[1-9]\d*))?)?$")


class ModelCatalogId(StrictStr):
    """A model catalog id."""


class PositiveCount(ConstrainedInt):
    """A positive count."""

    ge = 1
    strict = True


class NonNegativeCount(ConstrainedInt):
    """A non-negative count."""

    ge = 0
    strict = True


class Probability(ConstrainedFloat):
    """A probability value in [0, 1]."""

    ge = 0.0
    le = 1.0
    strict = True


class StatisticalTestOutcome(str, Enum):
    """A statistical test outcome."""

    reject_null_hypothesis = "reject null hypothesis"
    fail_to_reject_null_hypothesis = "fail to reject null hypothesis"


class DriftStatus(str, Enum):
    """A drift status."""

    drifted = "drifted"
    not_drifted = "not drifted"
