from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, SmallInteger, Date, Numeric, CHAR, ForeignKey, UniqueConstraint, Index, DateTime, func
from sqlalchemy.dialects.postgresql import CITEXT
from app.db import Base
from datetime import datetime, date

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String)
    email: Mapped[str] = mapped_column(CITEXT, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    trips: Mapped[list["Trip"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    currency_code: Mapped[str | None] = mapped_column(CHAR(3), index=True)
    total_budget: Mapped[float | None] = mapped_column(Numeric(12, 2))
    user: Mapped["User"] = relationship(back_populates="trips")
    items: Mapped[list["BudgetItem"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    targets: Mapped[list["TripBudgetTarget"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_trip_period", "start_date", "end_date"),)

class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)  # smallserial
    key: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    label: Mapped[str | None] = mapped_column(String)
    items: Mapped[list["BudgetItem"]] = relationship(back_populates="category")
    targets: Mapped[list["TripBudgetTarget"]] = relationship(back_populates="category")

class BudgetItem(Base):
    __tablename__ = "budget_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("budget_categories.id", ondelete="RESTRICT"), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String)
    planned_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    actual_amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    date: Mapped[date | None] = mapped_column(Date)
    trip: Mapped["Trip"] = relationship(back_populates="items")
    category: Mapped["BudgetCategory"] = relationship(back_populates="items")

class TripBudgetTarget(Base):
    __tablename__ = "trip_budget_targets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("budget_categories.id", ondelete="RESTRICT"), index=True, nullable=False)
    planned_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    trip: Mapped["Trip"] = relationship(back_populates="targets")
    category: Mapped["BudgetCategory"] = relationship(back_populates="targets")
    __table_args__ = (UniqueConstraint("trip_id", "category_id", name="uq_trip_category"),)
