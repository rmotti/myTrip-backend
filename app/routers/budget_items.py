# app/routers/budget_items.py
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import BudgetItem, BudgetCategory, Trip, User
from app.core.security import get_current_user
from app.schemas.budget import (
    BudgetItemCreate,
    BudgetItemOut,
    BudgetItemUpdate,
)


router = APIRouter(prefix="/trips/{trip_id}/items", tags=["budget_items"])


def _ensure_owner(trip: Trip, user_id: int) -> None:
    if trip.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a esta viagem.")


def _get_trip_or_404(db: Session, trip_id: int) -> Trip:
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrada.")
    return trip


def _validate_category(db: Session, category_id: int) -> None:
    if not db.query(BudgetCategory).filter(BudgetCategory.id == category_id).first():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Categoria inválida.")


@router.get("", response_model=list[BudgetItemOut])
def list_items(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    date_from: Optional[date] = Query(None, description="Filtra itens com date >= date_from"),
    date_until: Optional[date] = Query(None, description="Filtra itens com date <= date_until"),
    category_id: Optional[int] = Query(None, description="Filtra por categoria"),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)
    q = db.query(BudgetItem).filter(BudgetItem.trip_id == trip_id)
    if date_from:
        q = q.filter(BudgetItem.date >= date_from)
    if date_until:
        q = q.filter(BudgetItem.date <= date_until)
    if category_id is not None:
        q = q.filter(BudgetItem.category_id == category_id)

    items = (
        q.order_by(BudgetItem.date.asc().nullslast(), BudgetItem.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items


@router.post("", response_model=BudgetItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    trip_id: int,
    payload: BudgetItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)

    _validate_category(db, payload.category_id)

    item = BudgetItem(
        trip_id=trip_id,
        category_id=payload.category_id,
        title=payload.title,
        planned_amount=payload.planned_amount,
        actual_amount=payload.actual_amount,
        date=payload.date,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=BudgetItemOut)
def update_item(
    trip_id: int,
    item_id: int,
    payload: BudgetItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)

    item = db.query(BudgetItem).filter(BudgetItem.id == item_id).first()
    if not item or item.trip_id != trip_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado.")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"] is not None:
        _validate_category(db, int(data["category_id"]))

    for field, value in data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=BudgetItemOut)
def get_item(
    trip_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)

    item = db.query(BudgetItem).filter(BudgetItem.id == item_id).first()
    if not item or item.trip_id != trip_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado.")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    trip_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)

    item = db.query(BudgetItem).filter(BudgetItem.id == item_id).first()
    if not item or item.trip_id != trip_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado.")

    db.delete(item)
    db.commit()
    return None