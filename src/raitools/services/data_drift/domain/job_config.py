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

    @validator("feature_mapping")
    def check_feature_mapping_is_not_empty(
        cls, value: Dict[str, JobConfigFeature]
    ) -> Dict[str, JobConfigFeature]:
        """Checks that keys in feature map match names in associated features."""
        if len(value) == 0:
            raise BadJobConfigError("Feature mapping is empty.")

        return value

    @validator("feature_mapping")
    def check_keys_match_feature_name(
        cls, value: Dict[str, JobConfigFeature]
    ) -> Dict[str, JobConfigFeature]:
        """Checks that keys in feature map match names in associated features."""
        for key, feature in value.items():
            if key != feature.name:
                raise BadJobConfigError(
                    f"Feature mapping key '{key}' does not match feature name '{feature.name}'"
                )

        return value


def find_unsupported_characters(value_string: str, search_string: str) -> bool:
    """Matches invalid characters.

    The search string is a regex to match what should *not* be in the value
    string.
    """
    search = re.compile(search_string).search
    has_unsupported_characters = bool(search(value_string))
    return has_unsupported_characters
