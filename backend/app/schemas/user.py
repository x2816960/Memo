from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserStatus(str, Enum):
    ACTIVE = "active"
    DISABLED = "disabled"


class UserBase(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    email: Optional[str] = None
    nickname: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=32)


class UserUpdate(BaseModel):
    email: Optional[str] = None
    nickname: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    status: UserStatus
    must_change_password: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=32)
