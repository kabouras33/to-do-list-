from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: constr(min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

class UserUpdate(UserBase):
    password: Optional[constr(min_length=8)] = None

    @validator('password')
    def validate_password(cls, v):
        if v and not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if v and not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str