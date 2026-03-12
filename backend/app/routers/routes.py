from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.kc import KC
from app.models.prereq_edge import PrereqEdge
from app.models.mastery import Mastery
from app.models.route import Route
from app.schemas.route import RouteCreate, RouteOut
from app.services.routing import build_prereq_graph, compute_route, find_reroute_target

router = APIRouter()


def _build_route_out(route: Route, db: Session) -> RouteOut:
    goal_kc = db.query(KC).filter(KC.kc_id == route.goal_kc_id).first()
    kc_map: dict[int, str] = {kc.kc_id: kc.name for kc in db.query(KC).all()}

    next_kc_name = kc_map.get(route.next_kc_id) if route.next_kc_id else None
    return RouteOut(
        route_id=route.route_id,
        learner_id=route.learner_id,
        goal_kc_id=route.goal_kc_id,
        goal_kc_name=goal_kc.name if goal_kc else "Unknown",
        ordered_kc_ids=route.ordered_kc_ids,
        ordered_kc_names=[kc_map.get(kid, "?") for kid in route.ordered_kc_ids],
        next_kc_id=route.next_kc_id,
        next_kc_name=next_kc_name,
        created_ts=route.created_ts,
        updated_ts=route.updated_ts,
    )


def _get_mastery_map(learner_id: str, db: Session) -> dict[int, float]:
    rows = db.query(Mastery).filter(Mastery.learner_id == learner_id).all()
    return {m.kc_id: m.p_mastery for m in rows}


def _get_prereq_graph(db: Session) -> dict[int, list[int]]:
    edges = db.query(PrereqEdge).all()
    return build_prereq_graph([(e.from_kc_id, e.to_kc_id) for e in edges])


@router.post("/routes", response_model=RouteOut, status_code=201)
def create_or_refresh_route(payload: RouteCreate, db: Session = Depends(get_db)):
    goal_kc = db.query(KC).filter(KC.kc_id == payload.goal_kc_id).first()
    if not goal_kc:
        raise HTTPException(status_code=404, detail=f"KC {payload.goal_kc_id} not found")

    mastery_map = _get_mastery_map(payload.learner_id, db)
    prereq_graph = _get_prereq_graph(db)

    ordered = compute_route(payload.goal_kc_id, mastery_map, prereq_graph)
    next_kc_id = ordered[0] if ordered else None

    # Upsert route (replace existing for this learner)
    existing = db.query(Route).filter(Route.learner_id == payload.learner_id).first()
    now = datetime.now(timezone.utc)
    if existing:
        existing.goal_kc_id = payload.goal_kc_id
        existing.ordered_kc_ids = ordered
        existing.next_kc_id = next_kc_id
        existing.updated_ts = now
        route = existing
    else:
        route = Route(
            learner_id=payload.learner_id,
            goal_kc_id=payload.goal_kc_id,
            ordered_kc_ids=ordered,
            next_kc_id=next_kc_id,
            created_ts=now,
            updated_ts=now,
        )
        db.add(route)

    db.commit()
    db.refresh(route)
    return _build_route_out(route, db)


@router.get("/routes/{learner_id}", response_model=RouteOut)
def get_route(learner_id: str, db: Session = Depends(get_db)):
    route = db.query(Route).filter(Route.learner_id == learner_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="No active route found for this learner")
    return _build_route_out(route, db)


@router.post("/routes/{learner_id}/advance", response_model=RouteOut)
def advance_route(learner_id: str, db: Session = Depends(get_db)):
    """Mark the current KC as done and move to the next KC on the route."""
    route = db.query(Route).filter(Route.learner_id == learner_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="No active route found")

    ordered = list(route.ordered_kc_ids)
    current_id = route.next_kc_id

    if current_id in ordered:
        idx = ordered.index(current_id)
        # Move to next KC in the route
        if idx + 1 < len(ordered):
            route.next_kc_id = ordered[idx + 1]
        else:
            # Route complete — goal mastered
            route.next_kc_id = None
    else:
        # next_kc_id not in route — recompute
        mastery_map = _get_mastery_map(learner_id, db)
        prereq_graph = _get_prereq_graph(db)
        new_ordered = compute_route(route.goal_kc_id, mastery_map, prereq_graph)
        route.ordered_kc_ids = new_ordered
        route.next_kc_id = new_ordered[0] if new_ordered else None

    route.updated_ts = datetime.now(timezone.utc)
    db.commit()
    db.refresh(route)
    return _build_route_out(route, db)


@router.post("/routes/{learner_id}/reroute", response_model=RouteOut)
def reroute(learner_id: str, db: Session = Depends(get_db)):
    """Backtrack the route: move to the closest unmastered prerequisite."""
    route = db.query(Route).filter(Route.learner_id == learner_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="No active route found")

    mastery_map = _get_mastery_map(learner_id, db)
    prereq_graph = _get_prereq_graph(db)

    # Recompute route from current mastery state
    new_ordered = compute_route(route.goal_kc_id, mastery_map, prereq_graph)
    current_id = route.next_kc_id or (new_ordered[-1] if new_ordered else route.goal_kc_id)

    reroute_target = find_reroute_target(current_id, new_ordered, mastery_map)

    route.ordered_kc_ids = new_ordered
    route.next_kc_id = reroute_target
    route.updated_ts = datetime.now(timezone.utc)
    db.commit()
    db.refresh(route)
    return _build_route_out(route, db)
