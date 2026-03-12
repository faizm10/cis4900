from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.kc import KC
from app.models.prereq_edge import PrereqEdge
from app.schemas.kc import KCCreate, KCOut, KCUpdate, EdgeCreate, EdgeOut, GraphOut

router = APIRouter()


@router.get("/kcs", response_model=list[KCOut])
def list_kcs(db: Session = Depends(get_db)):
    return db.query(KC).order_by(KC.kc_id).all()


@router.get("/kcs/graph", response_model=GraphOut)
def get_graph(db: Session = Depends(get_db)):
    kcs = db.query(KC).order_by(KC.kc_id).all()
    edges = db.query(PrereqEdge).all()
    return GraphOut(kcs=kcs, edges=edges)


@router.get("/kcs/{kc_id}", response_model=KCOut)
def get_kc(kc_id: int, db: Session = Depends(get_db)):
    kc = db.query(KC).filter(KC.kc_id == kc_id).first()
    if not kc:
        raise HTTPException(status_code=404, detail="KC not found")
    return kc


@router.post("/kcs", response_model=KCOut, status_code=201)
def create_kc(payload: KCCreate, db: Session = Depends(get_db)):
    existing = db.query(KC).filter(KC.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="KC with this name already exists")
    kc = KC(**payload.model_dump())
    db.add(kc)
    db.commit()
    db.refresh(kc)
    return kc


@router.put("/kcs/{kc_id}", response_model=KCOut)
def update_kc(kc_id: int, payload: KCUpdate, db: Session = Depends(get_db)):
    kc = db.query(KC).filter(KC.kc_id == kc_id).first()
    if not kc:
        raise HTTPException(status_code=404, detail="KC not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(kc, field, value)
    db.commit()
    db.refresh(kc)
    return kc


@router.delete("/kcs/{kc_id}", status_code=204)
def delete_kc(kc_id: int, db: Session = Depends(get_db)):
    kc = db.query(KC).filter(KC.kc_id == kc_id).first()
    if not kc:
        raise HTTPException(status_code=404, detail="KC not found")
    db.delete(kc)
    db.commit()


# Prereq edge endpoints
@router.get("/edges", response_model=list[EdgeOut])
def list_edges(db: Session = Depends(get_db)):
    return db.query(PrereqEdge).all()


@router.post("/edges", response_model=EdgeOut, status_code=201)
def create_edge(payload: EdgeCreate, db: Session = Depends(get_db)):
    # Validate KCs exist
    for kc_id in [payload.from_kc_id, payload.to_kc_id]:
        if not db.query(KC).filter(KC.kc_id == kc_id).first():
            raise HTTPException(status_code=404, detail=f"KC {kc_id} not found")
    # Check for duplicate
    existing = db.query(PrereqEdge).filter(
        PrereqEdge.from_kc_id == payload.from_kc_id,
        PrereqEdge.to_kc_id == payload.to_kc_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Edge already exists")
    edge = PrereqEdge(**payload.model_dump())
    db.add(edge)
    db.commit()
    db.refresh(edge)
    return edge


@router.delete("/edges/{edge_id}", status_code=204)
def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    edge = db.query(PrereqEdge).filter(PrereqEdge.edge_id == edge_id).first()
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    db.delete(edge)
    db.commit()
