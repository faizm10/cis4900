from datetime import datetime
from pydantic import BaseModel


class MasteryEntry(BaseModel):
    kc_id: int
    kc_name: str
    p_mastery: float
    attempt_count: int
    status: str  # "locked" | "available" | "in_progress" | "mastered"
    updated_ts: datetime | None = None

    model_config = {"from_attributes": True}


class MasteryResponse(BaseModel):
    learner_id: str
    masteries: list[MasteryEntry]
