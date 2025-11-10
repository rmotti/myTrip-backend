from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, condecimal, constr, ConfigDict, field_serializer

# Casa com NUMERIC(12,2) do banco
Money = condecimal(max_digits=12, decimal_places=2)

# ---- Budget Categories ----
class BudgetCategoryOut(BaseModel):
    id: int
    key: str
    label: Optional[str] = None

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True)


# ---- Budget Items ----
class BudgetItemBase(BaseModel):
    category_id: Optional[int] = Field(None, description="Categoria do item")
    title: Optional[constr(min_length=1)] = None
    planned_amount: Optional[Money] = None
    actual_amount: Optional[Money] = None
    date: Optional[date] = None


class BudgetItemCreate(BaseModel):
    category_id: int
    title: constr(min_length=1)
    planned_amount: Money
    # default 0.00 evita 422 quando o front não mandar este campo
    actual_amount: Money = Field(default=Decimal("0.00"))
    date: Optional[date] = None


class BudgetItemUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[constr(min_length=1)] = None
    planned_amount: Optional[Money] = None
    actual_amount: Optional[Money] = None
    date: Optional[date] = None


class BudgetItemOut(BaseModel):
    id: int
    trip_id: int
    category_id: int
    title: str
    planned_amount: Money
    actual_amount: Money
    date: Optional[date] = None

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("planned_amount", "actual_amount", when_used="json")
    def _ser_money(self, v):
        return float(v) if v is not None else 0.0


# ---- Trip Budget Targets ----
class TripBudgetTargetBase(BaseModel):
    category_id: int
    planned_amount: Money


class TripBudgetTargetCreate(TripBudgetTargetBase):
    pass


class TripBudgetTargetUpdate(BaseModel):
    planned_amount: Optional[Money] = None


class TripBudgetTargetOut(BaseModel):
    id: int
    trip_id: int
    category_id: int
    planned_amount: Money

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("planned_amount", when_used="json")
    def _ser_money(self, v):
        return float(v) if v is not None else 0.0
