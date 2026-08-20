from app.models.order import OrderStatus
from pydantic import BaseModel, ConfigDict, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel): 
    id: int
    buyer_id: int
    status: OrderStatus
    total: float
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
    
class OrderStatusUpdate(BaseModel):
    status: OrderStatus