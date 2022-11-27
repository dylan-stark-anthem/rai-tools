"""Data drift report data model."""


from typing import Any, Dict, List

from pydantic import BaseModel, Field

import raitools
from raitools.services.data_drift.domain.types import (
    DatasetName,
    DatasetVersion,
    ModelCatalogId,
    PositiveCount,
    ReportName,
)


class ReportRecordMetadata(BaseModel):
    """Metadata for data drift record."""

    raitools_version: str = Field(raitools.__version__, const=True)


class DataDriftReportRecord(BaseModel):
    """Data drift report record."""

    apiVersion: str = Field("raitools/v1", const=True)
    kind: str = Field("DataDriftReportRecord", const=True)
    metadata: ReportRecordMetadata
    report_name: ReportName
    dataset_name: DatasetName
    dataset_version: DatasetVersion
    model_catalog_id: ModelCatalogId
    num_rows_baseline_data: PositiveCount
    num_columns_baseline_data: PositiveCount
    num_rows_test_data: PositiveCount
    num_columns_test_data: PositiveCount
    thresholds: Dict[str, Dict[str, float]]
    fields: List[str]
    observations: Dict[str, Any]

    class Config:
        """Configuration."""

        use_enum_value = True
