# app/routers/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.core.security import get_current_user
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_me(current: User = Depends(get_current_user)):
    return current

@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    if payload.name is not None:
        current.name = payload.name
    if payload.photo_url is not None:
        current.photo_url = str(payload.photo_url)
    db.commit()
    db.refresh(current)
    return current

@router.delete("/me", status_code=204)
def deactivate_me(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    current.is_active = False
    db.commit()
    return
