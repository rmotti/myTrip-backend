# app/routers/trips.py
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Trip, User
from app.schemas.trip import TripCreate, TripOut, TripUpdate
from app.core.security import decode_access_token  # assume que existe; ajuste se o seu projeto usar outro nome

router = APIRouter(prefix="/trips", tags=["trips"])
bearer = HTTPBearer()


# ---- Helpers ----
def _validate_dates(start: Optional[date], end: Optional[date]) -> None:
    if start and end and end < start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date não pode ser anterior a start_date."
        )


def _ensure_owner(trip: Trip, user_id: int) -> None:
    if trip.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a esta viagem.")


# ---- Auth dependency (JWT) ----
def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Lê o token Bearer (JWT), decodifica e retorna o usuário.
    O token deve conter, no mínimo, o claim 'sub' com o user_id.
    """
    token = creds.credentials
    try:
        payload = decode_access_token(token)  # -> dict com 'sub' (user_id)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
    return user


# ---- Endpoints ----

@router.get("", response_model=List[TripOut])
def list_my_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    start_from: Optional[date] = Query(None, description="Filtra viagens com start_date >= start_from"),
    end_until: Optional[date] = Query(None, description="Filtra viagens com end_date <= end_until"),
):
    """
    Lista as viagens do usuário autenticado com paginação e filtros de período.
    """
    q = db.query(Trip).filter(Trip.user_id == current_user.id)

    if start_from:
        q = q.filter(Trip.start_date >= start_from)
    if end_until:
        q = q.filter(Trip.end_date <= end_until)

    trips = q.order_by(Trip.start_date.desc().nullslast()).offset(skip).limit(limit).all()
    return trips


@router.get("/{trip_id}", response_model=TripOut)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrada.")
    _ensure_owner(trip, current_user.id)
    return trip


@router.post("", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(
    payload: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _validate_dates(payload.start_date, payload.end_date)

    trip = Trip(
        user_id=current_user.id,
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        currency_code=payload.currency_code,
        total_budget=payload.total_budget,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


@router.put("/{trip_id}", response_model=TripOut)
def update_trip(
    trip_id: int,
    payload: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrada.")
    _ensure_owner(trip, current_user.id)

    # Validação de datas com parciais
    new_start = payload.start_date if payload.start_date is not None else trip.start_date
    new_end = payload.end_date if payload.end_date is not None else trip.end_date
    _validate_dates(new_start, new_end)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(trip, field, value)

    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viagem não encontrada.")
    _ensure_owner(trip, current_user.id)

    db.delete(trip)
    db.commit()
    return None
