"""Types of data drift."""

import re

from pydantic import ConstrainedFloat, ConstrainedStr


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
