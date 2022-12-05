"""Exceptions for Data Drift."""


from typing import Any


class DataDriftError(Exception):
    """A Data Drift error."""

    def __init__(self, *args: Any) -> None:
        """Initializes."""
        super().__init__(self.__doc__, *args)
        self.code: int


class BadPathToBundleError(DataDriftError):
    """Bad path to bundle error."""

    code = 501


class BadBundleZipFileError(DataDriftError):
    """Bad bundle zip file error."""

    code = 502


class BadDataFileError(DataDriftError):
    """Bad data file error."""

    code = 503


class BadJobConfigError(DataDriftError):
    """Bad job config error."""

    code = 504


class BadFeatureMappingError(DataDriftError):
    """Bad feature mapping error."""

    code = 505


class BadRecordError(DataDriftError):
    """Bad record error."""

    code = 506
