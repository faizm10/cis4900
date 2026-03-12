from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.item import Item
from app.models.attempt import Attempt
from app.models.kc import KC
from app.schemas.item import ItemCreate, ItemUpdate, ItemPublic, ItemWithAnswer

router = APIRouter()


@router.get("/items", response_model=list[ItemWithAnswer])
def list_items(kc_id: int | None = Query(None), db: Session = Depends(get_db)):
    q = db.query(Item)
    if kc_id:
        q = q.filter(Item.kc_id == kc_id)
    return q.order_by(Item.item_id).all()


@router.get("/items/next", response_model=ItemPublic)
def get_next_item(
    learner_id: str = Query(...),
    kc_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Returns the next item for a learner on a given KC.
    Excludes the 3 most recently seen items for this learner+KC to promote variety.
    """
    # Get IDs of recently seen items
    recent_attempts = (
        db.query(Attempt.item_id)
        .filter(Attempt.learner_id == learner_id, Attempt.kc_id == kc_id)
        .order_by(Attempt.timestamp.desc())
        .limit(3)
        .all()
    )
    recent_ids = [r.item_id for r in recent_attempts]

    # Prefer items not recently seen
    q = db.query(Item).filter(Item.kc_id == kc_id)
    unseen = q.filter(Item.item_id.notin_(recent_ids)).order_by(Item.item_id).first()
    if unseen:
        return unseen

    # Fall back to any item for this KC
    item = q.order_by(Item.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"No items found for KC {kc_id}")
    return item


@router.get("/items/kc/{kc_id}", response_model=list[ItemPublic])
def get_items_by_kc(kc_id: int, db: Session = Depends(get_db)):
    items = db.query(Item).filter(Item.kc_id == kc_id).all()
    return items


@router.get("/items/{item_id}", response_model=ItemWithAnswer)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/items", response_model=ItemWithAnswer, status_code=201)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    if not db.query(KC).filter(KC.kc_id == payload.kc_id).first():
        raise HTTPException(status_code=404, detail=f"KC {payload.kc_id} not found")
    item = Item(
        kc_id=payload.kc_id,
        prompt=payload.prompt,
        type=payload.type,
        choices=[c.model_dump() for c in payload.choices] if payload.choices else None,
        answer=payload.answer,
        difficulty=payload.difficulty,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=ItemWithAnswer)
def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    data = payload.model_dump(exclude_none=True)
    if "choices" in data and data["choices"] is not None:
        data["choices"] = [c.model_dump() for c in payload.choices]
    for field, value in data.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
