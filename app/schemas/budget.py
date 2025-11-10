from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ---- Budget Categories ----
class BudgetCategoryOut(BaseModel):
    id: int
    key: str
    label: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---- Budget Items ----
class BudgetItemBase(BaseModel):
    category_id: Optional[int] = Field(None, description="Categoria do item")
    title: Optional[str] = None
    planned_amount: Optional[float] = None
    actual_amount: Optional[float] = None
    date: Optional[date] = None


class BudgetItemCreate(BudgetItemBase):
    category_id: int


class BudgetItemUpdate(BudgetItemBase):
    pass


class BudgetItemOut(BudgetItemBase):
    id: int
    trip_id: int

    model_config = ConfigDict(from_attributes=True)


# ---- Trip Budget Targets ----
class TripBudgetTargetBase(BaseModel):
    category_id: int
    planned_amount: float


class TripBudgetTargetCreate(TripBudgetTargetBase):
    pass


class TripBudgetTargetUpdate(BaseModel):
    planned_amount: Optional[float] = None


class TripBudgetTargetOut(BaseModel):
    id: int
    trip_id: int
    category_id: int
    planned_amount: float

    model_config = ConfigDict(from_attributes=True)
