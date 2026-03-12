from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.kc import KC
from app.models.prereq_edge import PrereqEdge
from app.models.mastery import Mastery
from app.schemas.mastery import MasteryEntry, MasteryResponse
from app.services.bkt import TAU_MASTERY

router = APIRouter()


def derive_status(
    kc_id: int,
    mastery_map: dict[int, float],
    attempt_map: dict[int, int],
    prereq_graph: dict[int, list[int]],
) -> str:
    """
    Derive node status from mastery + prereq graph.
    - mastered:    p_mastery >= TAU_MASTERY
    - in_progress: any attempts but not mastered
    - available:   all prereqs mastered, no attempts yet
    - locked:      at least one prereq not mastered
    """
    p = mastery_map.get(kc_id, 0.0)
    if p >= TAU_MASTERY:
        return "mastered"

    if attempt_map.get(kc_id, 0) > 0:
        return "in_progress"

    prereqs = prereq_graph.get(kc_id, [])
    if all(mastery_map.get(prereq, 0.0) >= TAU_MASTERY for prereq in prereqs):
        return "available"

    return "locked"


@router.get("/mastery", response_model=MasteryResponse)
def get_mastery(learner_id: str = Query(...), db: Session = Depends(get_db)):
    all_kcs = db.query(KC).order_by(KC.kc_id).all()
    all_edges = db.query(PrereqEdge).all()
    mastery_rows = db.query(Mastery).filter(Mastery.learner_id == learner_id).all()

    # Build lookup maps
    mastery_map: dict[int, float] = {m.kc_id: m.p_mastery for m in mastery_rows}
    attempt_map: dict[int, int] = {m.kc_id: m.attempt_count for m in mastery_rows}
    mastery_ts_map: dict[int, object] = {m.kc_id: m.updated_ts for m in mastery_rows}

    # prereq_graph: kc_id -> [prereq_kc_ids]
    prereq_graph: dict[int, list[int]] = {kc.kc_id: [] for kc in all_kcs}
    for edge in all_edges:
        prereq_graph.setdefault(edge.to_kc_id, []).append(edge.from_kc_id)

    entries = []
    for kc in all_kcs:
        status = derive_status(kc.kc_id, mastery_map, attempt_map, prereq_graph)
        entries.append(MasteryEntry(
            kc_id=kc.kc_id,
            kc_name=kc.name,
            p_mastery=mastery_map.get(kc.kc_id, kc.p_l0),
            attempt_count=attempt_map.get(kc.kc_id, 0),
            status=status,
            updated_ts=mastery_ts_map.get(kc.kc_id),
        ))

    return MasteryResponse(learner_id=learner_id, masteries=entries)


@router.get("/mastery/{learner_id}/{kc_id}", response_model=MasteryEntry)
def get_mastery_for_kc(learner_id: str, kc_id: int, db: Session = Depends(get_db)):
    kc = db.query(KC).filter(KC.kc_id == kc_id).first()
    if not kc:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="KC not found")

    all_edges = db.query(PrereqEdge).all()
    mastery_rows = db.query(Mastery).filter(Mastery.learner_id == learner_id).all()
    mastery_map = {m.kc_id: m.p_mastery for m in mastery_rows}
    attempt_map = {m.kc_id: m.attempt_count for m in mastery_rows}

    prereq_graph: dict[int, list[int]] = {}
    for edge in all_edges:
        prereq_graph.setdefault(edge.to_kc_id, []).append(edge.from_kc_id)

    mastery_row = db.query(Mastery).filter(
        Mastery.learner_id == learner_id, Mastery.kc_id == kc_id
    ).first()

    status = derive_status(kc_id, mastery_map, attempt_map, prereq_graph)
    return MasteryEntry(
        kc_id=kc_id,
        kc_name=kc.name,
        p_mastery=mastery_row.p_mastery if mastery_row else kc.p_l0,
        attempt_count=mastery_row.attempt_count if mastery_row else 0,
        status=status,
        updated_ts=mastery_row.updated_ts if mastery_row else None,
    )


@router.delete("/mastery/{learner_id}", status_code=204)
def reset_mastery(learner_id: str, db: Session = Depends(get_db)):
    """Demo reset: wipe all mastery data for a learner."""
    db.query(Mastery).filter(Mastery.learner_id == learner_id).delete()
    db.commit()
