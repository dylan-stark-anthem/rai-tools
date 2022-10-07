"""A Data Drift job config."""

from typing import Dict
from pydantic import BaseModel


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