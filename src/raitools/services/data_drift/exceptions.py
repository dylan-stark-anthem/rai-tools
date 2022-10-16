"""Exceptions for Data Drift."""


from typing import Dict, Optional


class BadPathToBundleError(Exception):
    """Bad path to bundle error."""

    def __init__(self, message: str, info: Optional[Dict] = None) -> None:
        """Initializes exception and sets extra info if provided."""
        super().__init__(message)
        self.info = info if info else {}
