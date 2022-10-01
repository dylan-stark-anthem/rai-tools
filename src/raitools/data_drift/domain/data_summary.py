"""A dataset summary."""


from pydantic import BaseModel


class DataSummary(BaseModel):
    """Summary statistics for a dataset."""

    num_rows: int
    num_columns: int
