from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.kc import KC
from app.models.attempt import Attempt
from app.models.mastery import Mastery

router = APIRouter()


@router.get("/admin/stats")
def get_stats(db: Session = Depends(get_db)):
    learner_count = db.query(func.count(func.distinct(Attempt.learner_id))).scalar()
    attempt_count = db.query(func.count(Attempt.attempt_id)).scalar()

    # Average mastery per KC
    kcs = db.query(KC).order_by(KC.kc_id).all()
    kc_stats = []
    for kc in kcs:
        avg = db.query(func.avg(Mastery.p_mastery)).filter(Mastery.kc_id == kc.kc_id).scalar()
        cnt = db.query(func.count(Mastery.mastery_id)).filter(Mastery.kc_id == kc.kc_id).scalar()
        kc_stats.append({
            "kc_id": kc.kc_id,
            "kc_name": kc.name,
            "learner_count": cnt,
            "avg_mastery": round(float(avg), 4) if avg else 0.0,
        })

    return {
        "learner_count": learner_count,
        "attempt_count": attempt_count,
        "kc_stats": kc_stats,
    }


@router.post("/admin/seed")
def run_seed(db: Session = Depends(get_db)):
    """Idempotent seed — inserts missing KCs, edges, and items."""
    from app.seed.seed_data import seed
    seed()
    kc_count = db.query(func.count(KC.kc_id)).scalar()
    return {"message": "Seed complete", "kc_count": kc_count}
