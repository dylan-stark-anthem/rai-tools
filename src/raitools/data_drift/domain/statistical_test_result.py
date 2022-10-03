"""Statistical test result."""


from pydantic import BaseModel


class StatisticalTestResult(BaseModel):
    """Results of a statistical test."""

    statistic: float
    p_value: float
