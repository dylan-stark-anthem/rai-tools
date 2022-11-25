"""A Data Drift feature mapping."""

from typing import Dict

from pydantic import BaseModel, validator

from raitools.services.data_drift.domain.types import ImportanceScore
from raitools.services.data_drift.exceptions import BadFeatureMappingError


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
