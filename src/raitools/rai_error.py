"""RAI error."""


from pydantic import BaseModel, Field

import raitools


class Metadata(BaseModel):
    """FAITH record metadata."""

    faith_version: str = Field(raitools.__version__, const=True)


class RaiError(BaseModel):
    """An RAI error."""

    api_version: str = Field("rai-tools/v1.0.0", const=True)
    kind: str = Field("RaiError")
    metadata: Metadata = Metadata()

    message: str
