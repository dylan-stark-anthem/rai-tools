"""A Data Drift job config."""

import re
from typing import Dict
from pydantic import BaseModel, validator

from raitools.services.data_drift.exceptions import BadJobConfigError


class JobConfigFeature(BaseModel):
    """A feature."""

    name: str
    kind: str
    rank: int


class DataDriftJobConfig(BaseModel):
    """A Data Drift job config."""

    report_name: str
    dataset_name: str
    dataset_version: str
    baseline_data_filename: str
    test_data_filename: str
    model_catalog_id: str
    feature_mapping: Dict[str, JobConfigFeature]

    @validator("report_name")
    def check_report_name(cls, value: str) -> str:
        """Checks that report is valid."""
        if value == "":
            raise BadJobConfigError("Report name is empty.")

        if find_unsupported_characters(value[0], r"[^a-zA-Z]"):
            raise BadJobConfigError(
                f"Report name '{value}' does not start with `[a-zA-Z]`."
            )

        if find_unsupported_characters(value, r"[^A-Za-z0-9. _]"):
            raise BadJobConfigError(
                f"Report name '{value}' contains unsupported characters."
            )

        if value[-1] == " ":
            raise BadJobConfigError("Report name 'a ' ends with a space.")

        return value


def find_unsupported_characters(value_string: str, search_string: str) -> bool:
    """Matches invalid characters.

    The search string is a regex to match what should *not* be in the value
    string.
    """
    search = re.compile(search_string).search
    has_unsupported_characters = bool(search(value_string))
    return has_unsupported_characters
