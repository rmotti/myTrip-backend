from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date


# Base (campos comuns)
class TripBase(BaseModel):
    name: Optional[str] = Field(None, example="Viagem a Paris")
    destination: Optional[str] = Field(None, example="Paris, França")
    start_date: Optional[date] = Field(None, example="2025-03-10")
    end_date: Optional[date] = Field(None, example="2025-03-17")
    currency_code: Optional[str] = Field(None, example="BRL", min_length=3, max_length=3)
    total_budget: Optional[float] = Field(None, example=5000.00)


# Criação (campos obrigatórios mínimos)
class TripCreate(TripBase):
    name: str
    start_date: date
    end_date: date
    currency_code: str


# Atualização (todos opcionais)
class TripUpdate(TripBase):
    pass


# Saída (resposta)
class TripOut(TripBase):
    id: int
    user_id: int

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True)  # mapeia direto do modelo SQLAlchemy
