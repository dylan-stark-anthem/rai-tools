"""Exceptions for Data Drift."""


class BadPathToBundleError(Exception):
    """Bad path to bundle error."""


class BadBundleZipFileError(Exception):
    """Bad bundle zip file error."""


class BadDataFileError(Exception):
    """Bad data file error."""


class BadJobConfigError(Exception):
    """Bad job config error."""


class BadFeatureMappingError(Exception):
    """Bad feature mapping error."""
