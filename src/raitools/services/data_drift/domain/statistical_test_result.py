"""Statistical test result."""


from pydantic import BaseModel


class StatisticalTestResult(BaseModel):
    """Results of a statistical test."""

    test_statistic: float
    p_value: float
