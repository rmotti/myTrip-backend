# app/routers/trip_budget_targets.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import TripBudgetTarget, Trip, BudgetCategory, User
from app.core.security import get_current_user
from app.schemas.budget import (
    TripBudgetTargetCreate,
    TripBudgetTargetOut,
)


router = APIRouter(prefix="/trips/{trip_id}/targets", tags=["trip_budget_targets"])


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


@router.get("", response_model=list[TripBudgetTargetOut])
def list_targets(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)
    targets = (
        db.query(TripBudgetTarget)
        .filter(TripBudgetTarget.trip_id == trip_id)
        .order_by(TripBudgetTarget.category_id.asc())
        .all()
    )
    return targets


@router.post("", response_model=TripBudgetTargetOut, status_code=status.HTTP_201_CREATED)
def upsert_target(
    trip_id: int,
    payload: TripBudgetTargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)

    _validate_category(db, payload.category_id)

    target = (
        db.query(TripBudgetTarget)
        .filter(
            TripBudgetTarget.trip_id == trip_id,
            TripBudgetTarget.category_id == payload.category_id,
        )
        .first()
    )

    if target is None:
        target = TripBudgetTarget(
            trip_id=trip_id,
            category_id=payload.category_id,
            planned_amount=payload.planned_amount,
        )
        db.add(target)
    else:
        target.planned_amount = payload.planned_amount

    db.commit()
    db.refresh(target)
    return target


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_target(
    trip_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)

    target = (
        db.query(TripBudgetTarget)
        .filter(
            TripBudgetTarget.trip_id == trip_id,
            TripBudgetTarget.category_id == category_id,
        )
        .first()
    )
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta não encontrada.")

    db.delete(target)
    db.commit()
    return None


@router.get("/{category_id}", response_model=TripBudgetTargetOut)
def get_target(
    trip_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)

    target = (
        db.query(TripBudgetTarget)
        .filter(
            TripBudgetTarget.trip_id == trip_id,
            TripBudgetTarget.category_id == category_id,
        )
        .first()
    )
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta não encontrada.")
    return target
