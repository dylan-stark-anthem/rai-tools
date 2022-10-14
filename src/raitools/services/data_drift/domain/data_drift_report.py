"""Data drift report data model."""


from typing import Any, Dict, List
from pydantic import BaseModel


class ReportRecordMetadata(BaseModel):
    """Metadata for data drift record."""

    raitools_version: str


class DataDriftReportRecord(BaseModel):
    """Data drift report record."""

    apiVersion: str = "raitools/v1"
    kind: str = "DataDriftReportRecord"
    metadata: ReportRecordMetadata
    report_name: str
    dataset_name: str
    dataset_version: str
    model_catalog_id: str
    num_rows_baseline_data: int
    num_columns_baseline_data: int
    num_rows_test_data: int
    num_columns_test_data: int
    num_numerical_features: int
    num_categorical_features: int
    thresholds: Dict[str, Dict[str, float]]
    num_total_features: int
    num_features_drifted: int
    top_10_features_drifted: int
    top_20_features_drifted: int
    fields: List[str]
    observations: Dict[str, Any]
