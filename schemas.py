from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_seller: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: int
    seller_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class CommissionResponse(BaseModel):
    id: int
    order_id: int
    seller_id: int
    amount: float
    commission_rate: float
    commission_amount: float
    seller_amount: float
    created_at: datetime

    class Config:
        from_attributes = True

