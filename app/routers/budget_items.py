# app/routers/budget_items.py
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
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


def _parse_date(value) -> Optional[date]:
    if value in (None, "", "null"):
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        # aceita "YYYY-MM-DD"
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
        # aceita ISO com hora: "YYYY-MM-DDTHH:MM:SSZ"
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except Exception:
            pass
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Formato de data inválido (use YYYY-MM-DD ou null).")


def _to_number(value, field_name: str) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "."))
        except ValueError:
            pass
    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Campo '{field_name}' deve ser numérico.")


def _normalize_create_payload(raw: dict) -> dict:
    """
    Aceita payload 'limpo' (create) ou 'cheio' (com id/trip_id) e normaliza.
    Ignora chaves somente de saída: id, trip_id.
    """
    if not isinstance(raw, dict):
        raise HTTPException(status_code=422, detail="JSON inválido.")

    # obrigatórios
    if "category_id" not in raw:
        raise HTTPException(status_code=422, detail="Campo 'category_id' é obrigatório.")
    if "title" not in raw or not (raw.get("title") or "").strip():
        raise HTTPException(status_code=422, detail="Campo 'title' é obrigatório.")
    if "planned_amount" not in raw:
        raise HTTPException(status_code=422, detail="Campo 'planned_amount' é obrigatório.")

    category_id = raw.get("category_id")
    try:
        category_id = int(category_id)
    except Exception:
        raise HTTPException(status_code=422, detail="Campo 'category_id' deve ser inteiro.")

    title = (raw.get("title") or "").strip()

    planned_amount = _to_number(raw.get("planned_amount"), "planned_amount")
    actual_amount = _to_number(raw.get("actual_amount", 0), "actual_amount")

    date_value = _parse_date(raw.get("date"))

    return {
        "category_id": category_id,
        "title": title,
        "planned_amount": planned_amount,
        "actual_amount": actual_amount,
        "date": date_value,
    }


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
    raw_payload: dict = Body(..., description="Aceita formato 'limpo' ou 'cheio' (com id/trip_id)."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cria um item de orçamento. Ignora 'id' e 'trip_id' enviados no corpo.
    Aceita:
    - {category_id, title, planned_amount, actual_amount?, date?}
    - {id?, trip_id?, category_id, title, planned_amount, actual_amount?, date?}
    """
    trip = _get_trip_or_404(db, trip_id)
    _ensure_owner(trip, current_user.id)

    data = _normalize_create_payload(raw_payload)
    _validate_category(db, data["category_id"])

    item = BudgetItem(
        trip_id=trip_id,  # força trip_id da URL
        category_id=data["category_id"],
        title=data["title"],
        planned_amount=data["planned_amount"],
        actual_amount=data["actual_amount"],
        date=data["date"],  # pode ser None
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

    if "date" in data:
        data["date"] = _parse_date(data["date"])

    if "planned_amount" in data:
        data["planned_amount"] = _to_number(data["planned_amount"], "planned_amount")
    if "actual_amount" in data:
        data["actual_amount"] = _to_number(data["actual_amount"], "actual_amount")

    if "category_id" in data and data["category_id"] is not None:
        try:
            data["category_id"] = int(data["category_id"])
        except Exception:
            raise HTTPException(status_code=422, detail="Campo 'category_id' deve ser inteiro.")
        _validate_category(db, int(data["category_id"]))

    for field, value in data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item
