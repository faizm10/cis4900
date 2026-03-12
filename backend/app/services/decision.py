"""
Decision service: orchestrates BKT update, mastery persistence, and policy decision.
Called by the attempts router after receiving a learner's response.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.kc import KC
from app.models.item import Item
from app.models.attempt import Attempt
from app.models.mastery import Mastery
from app.services.bkt import bkt_update, decide


def process_attempt(
    db: Session,
    learner_id: str,
    item_id: int,
    kc_id: int,
    response: str,
) -> dict:
    """
    Process a learner's response:
    1. Validate item + KC
    2. Compute correctness
    3. Run BKT update
    4. Persist attempt + mastery
    5. Return decision payload
    """
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        raise ValueError(f"Item {item_id} not found")

    kc = db.query(KC).filter(KC.kc_id == kc_id).first()
    if not kc:
        raise ValueError(f"KC {kc_id} not found")

    correct = response.strip().upper() == item.answer.strip().upper()

    # Fetch or initialize mastery record
    mastery_row = db.query(Mastery).filter(
        Mastery.learner_id == learner_id,
        Mastery.kc_id == kc_id,
    ).first()

    p_mastery_before = mastery_row.p_mastery if mastery_row else kc.p_l0
    attempt_count_before = mastery_row.attempt_count if mastery_row else 0

    # BKT update
    p_mastery_after = bkt_update(
        p_l=p_mastery_before,
        correct=correct,
        p_t=kc.p_t,
        p_g=kc.p_g,
        p_s=kc.p_s,
    )

    new_attempt_count = attempt_count_before + 1
    decision = decide(p_mastery_after, new_attempt_count)

    # Persist attempt
    attempt = Attempt(
        learner_id=learner_id,
        item_id=item_id,
        kc_id=kc_id,
        correctness=correct,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(attempt)

    # Upsert mastery
    if mastery_row:
        mastery_row.p_mastery = p_mastery_after
        mastery_row.attempt_count = new_attempt_count
        mastery_row.updated_ts = datetime.now(timezone.utc)
    else:
        db.add(Mastery(
            learner_id=learner_id,
            kc_id=kc_id,
            p_mastery=p_mastery_after,
            attempt_count=new_attempt_count,
            updated_ts=datetime.now(timezone.utc),
        ))

    db.flush()

    attempt_id = attempt.attempt_id

    # Build feedback string
    if correct:
        feedback = f"Correct! Well done."
    else:
        feedback = f"Incorrect. The correct answer was: {item.answer}."

    db.commit()

    return {
        "attempt_id": attempt_id,
        "correct": correct,
        "correct_answer": item.answer,
        "p_mastery_before": round(p_mastery_before, 4),
        "p_mastery_after": round(p_mastery_after, 4),
        "decision": decision,
        "next_kc_id": kc_id,  # routing layer updates this if reroute/advance
        "feedback": feedback,
    }
