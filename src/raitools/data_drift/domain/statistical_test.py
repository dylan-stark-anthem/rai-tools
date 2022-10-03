"""Statistical test for data drift."""


from pydantic import BaseModel


class StatisticalTest(BaseModel):
    """A statistical test."""

    name: str
    threshold: float
