from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    tg_id: str
    username: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    balance: float
    created_at: datetime
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    amount: float
    package_type: str

class OrderResponse(BaseModel):
    id: int
    amount: float
    credits: float
    package_type: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True
