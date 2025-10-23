# app/schemas/auth.py
from pydantic import BaseModel


class TokenOut(BaseModel):
    access_token: str
    token_type: str
    expires_in_min: int

