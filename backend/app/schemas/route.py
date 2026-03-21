from datetime import datetime
from pydantic import BaseModel


class RouteCreate(BaseModel):
    learner_id: str
    goal_kc_id: int


class RouteOut(BaseModel):
    route_id: int
    learner_id: str
    goal_kc_id: int
    goal_kc_name: str
    ordered_kc_ids: list[int]
    ordered_kc_names: list[str]
    next_kc_id: int | None
    next_kc_name: str | None
    next_step_rationale: str
    created_ts: datetime
    updated_ts: datetime

    model_config = {"from_attributes": True}
