"""A Data Drift job config."""

from typing import List
from pydantic import BaseModel


class Feature(BaseModel):
    """A feature."""

    name: str
    kind: str


class JobConfig(BaseModel):
    """A Data Drift job config."""

    dataset_name: str
    baseline_data_filename: str
    test_data_filename: str
    model_catalog_id: str
    feature_mapping: List[Feature]
