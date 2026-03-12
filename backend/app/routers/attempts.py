from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attempt import Attempt
from app.schemas.attempt import AttemptSubmit, AttemptResponse, AttemptOut
from app.services.decision import process_attempt

router = APIRouter()


@router.post("/attempts", response_model=AttemptResponse)
def submit_attempt(payload: AttemptSubmit, db: Session = Depends(get_db)):
    """
    Core learning loop: submit a learner's answer, trigger BKT update,
    and return the decision (advance/remediate/reroute) with updated mastery.
    """
    try:
        result = process_attempt(
            db=db,
            learner_id=payload.learner_id,
            item_id=payload.item_id,
            kc_id=payload.kc_id,
            response=payload.response,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return AttemptResponse(**result)


@router.get("/attempts", response_model=list[AttemptOut])
def list_attempts(
    learner_id: str = Query(...),
    kc_id: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Attempt).filter(Attempt.learner_id == learner_id)
    if kc_id:
        q = q.filter(Attempt.kc_id == kc_id)
    return q.order_by(Attempt.timestamp.desc()).limit(limit).all()
