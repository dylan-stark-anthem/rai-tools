"""Data summary produced by data drift."""


from pydantic import BaseModel


class DataDriftDataSummary(BaseModel):
    """Summary statistics for data."""

    num_numerical_features: int
    num_categorical_features: int
