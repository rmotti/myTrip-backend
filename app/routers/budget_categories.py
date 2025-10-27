# app/routers/budget_categories.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import BudgetCategory, User
from app.core.security import get_current_user
from app.schemas.budget import BudgetCategoryOut


router = APIRouter(prefix="/budget-categories", tags=["budget_categories"])


@router.get("", response_model=list[BudgetCategoryOut])
def list_budget_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    categories = db.query(BudgetCategory).order_by(BudgetCategory.key.asc()).all()
    return categories

