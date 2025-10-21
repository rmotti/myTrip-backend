# app/schemas/user.py
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional

class UserBase(BaseModel):
    name: Optional[str] = None
    photo_url: Optional[HttpUrl] = None

class UserOut(UserBase):
    id: int
    email: EmailStr
    firebase_uid: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdate(UserBase):
    pass
