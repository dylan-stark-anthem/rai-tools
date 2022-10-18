"""Types of data drift."""

import re
from pydantic import ConstrainedInt, ConstrainedStr, StrictStr


class Rank(ConstrainedInt):
    """A rank."""

    ge = 1
    strict = True


class Name(ConstrainedStr):
    """A report name."""

    min_length = 1
    max_length = 128
    regex = re.compile(r"^[a-zA-Z][a-zA-Z0-9-._ ]*$")
    strict = True


class ReportName(Name):
    """A report name."""


class DatasetName(Name):
    """A dataset name."""


class FeatureName(Name):
    """A feature name."""


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
