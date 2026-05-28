from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    company_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str
