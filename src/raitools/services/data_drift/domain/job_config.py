"""A Data Drift job config."""

import re

from pydantic import BaseModel, validator

from raitools.services.data_drift.exceptions import BadJobConfigError


class DataDriftJobConfig(BaseModel):
    """A Data Drift job config."""

    service_name: str
    report_name: str
    dataset_name: str
    dataset_version: str
    feature_mapping_filename: str
    baseline_data_filename: str
    test_data_filename: str
    model_catalog_id: str

    @validator("service_name")
    def check_service_name(cls, value: str) -> str:
        """Checks that service name is set to "data_drift"."""
        if value != "data_drift":
            raise BadJobConfigError(
                f'Service name must be "data_drift"; user-provided "{value}" is not valid'
            )
        return value

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
