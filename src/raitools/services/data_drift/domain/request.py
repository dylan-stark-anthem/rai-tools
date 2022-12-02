"""Data Drift request."""

from pathlib import Path

from pydantic import BaseModel


class Request(BaseModel):
    """A Data Drift service response."""

    bundle_path: Path
    timestamp: str
    uuid: str
