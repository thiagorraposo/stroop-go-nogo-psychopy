"""Base fechada e estrita para os schemas HTTP, sem coercao de tipos."""

from pydantic import BaseModel, ConfigDict


class RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)
