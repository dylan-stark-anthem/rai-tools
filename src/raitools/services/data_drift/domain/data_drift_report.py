"""The data drift report."""

from typing import Any

from pydantic import BaseModel, Field

import raitools


class RecordMetadata(BaseModel):
    """Metadata for data drift record."""

    raitools_version: str = Field(raitools.__version__, const=True)


class DataDriftReport(BaseModel):
    """A Data Drift report."""

    apiVersion: str = Field("raitools/v1", const=True)
    kind: str = Field("DataDriftReport", const=True)
    metadata: RecordMetadata = Field(dict)
    results: Any
