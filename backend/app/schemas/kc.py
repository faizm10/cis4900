from datetime import datetime
from pydantic import BaseModel, Field


class KCBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str | None = None
    p_l0: float = Field(0.1, ge=0.0, le=1.0)
    p_t: float = Field(0.1, ge=0.0, le=1.0)
    p_g: float = Field(0.25, ge=0.0, le=1.0)
    p_s: float = Field(0.1, ge=0.0, le=1.0)


class KCCreate(KCBase):
    pass


class KCUpdate(BaseModel):
    name: str | None = Field(None, max_length=100)
    description: str | None = None
    p_l0: float | None = Field(None, ge=0.0, le=1.0)
    p_t: float | None = Field(None, ge=0.0, le=1.0)
    p_g: float | None = Field(None, ge=0.0, le=1.0)
    p_s: float | None = Field(None, ge=0.0, le=1.0)


class KCOut(KCBase):
    kc_id: int
    created_ts: datetime

    model_config = {"from_attributes": True}


class EdgeOut(BaseModel):
    edge_id: int
    from_kc_id: int
    to_kc_id: int

    model_config = {"from_attributes": True}


class EdgeCreate(BaseModel):
    from_kc_id: int
    to_kc_id: int


class GraphOut(BaseModel):
    kcs: list[KCOut]
    edges: list[EdgeOut]
