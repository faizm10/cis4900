from datetime import datetime
from pydantic import BaseModel


class AttemptSubmit(BaseModel):
    learner_id: str
    item_id: int
    kc_id: int
    response: str


class AttemptResponse(BaseModel):
    attempt_id: int
    correct: bool
    correct_answer: str
    p_mastery_before: float
    p_mastery_after: float
    decision: str  # "advance" | "remediate" | "reroute"
    next_kc_id: int | None
    feedback: str


class AttemptOut(BaseModel):
    attempt_id: int
    learner_id: str
    item_id: int
    kc_id: int
    correctness: bool
    timestamp: datetime

    model_config = {"from_attributes": True}
