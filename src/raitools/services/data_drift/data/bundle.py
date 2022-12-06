"""Data model for Data Drift bundle."""

from typing import Dict

import pyarrow as pa
from pydantic import BaseModel, validator

from raitools.exceptions import BadFeatureMappingError
from raitools.services.data_drift.data.job_config import DataDriftJobConfig
from raitools.services.data_drift.data.common import FileName, ImportanceScore


class Feature(BaseModel):
    """A feature."""

    name: str
    kind: str
    importance_score: ImportanceScore

    @validator("kind")
    def check_kind_supported(cls, value: str) -> str:  # noqa: B902
        """Checks whether provided kind is supported."""
        supported_kinds = ["numerical", "categorical"]
        if value not in supported_kinds:
            raise BadFeatureMappingError(
                f"Feature kind '{value}' is not supported. "
                "Supported feature kinds are 'numerical' and 'categorical."
            )

        return value


class FeatureMapping(BaseModel):
    """A feature mapping."""

    feature_mapping: Dict[str, Feature]

    @validator("feature_mapping")
    def check_feature_mapping_is_not_empty(
        cls, value: Dict[str, Feature]  # noqa: B902
    ) -> Dict[str, Feature]:
        """Checks that keys in feature map match names in associated features."""
        if len(value) == 0:
            raise BadFeatureMappingError("Feature mapping is empty.")

        return value


class Bundle(BaseModel):
    """A Data Drift bundle."""

    job_config_filename: FileName
    feature_mapping_filename: FileName
    baseline_data_filename: FileName
    test_data_filename: FileName
    job_config: DataDriftJobConfig
    feature_mapping: FeatureMapping
    baseline_data: pa.Table
    test_data: pa.Table

    class Config:
        """Configuration for bundle data model."""

        arbitrary_types_allowed = True
