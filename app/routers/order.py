from app.core.dependencies import get_current_user, require_role
from app.db.database import get_db
from app.models.user import RoleEnum, User
from app.schemas.order import OrderCreate, OrderResponse
from app.services import order as order_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.BUYER)),
):
    try:
        return order_service.create_order(db, order_in, buyer_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/me", response_model=list[OrderResponse])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.BUYER)),
):
    return order_service.get_buyer_orders(db, buyer_id=current_user.id)


@router.get("/seller", response_model=list[OrderResponse])
def get_seller_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(RoleEnum.SELLER)),
):
    return order_service.get_seller_orders(db, seller_id=current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if not order_service.user_can_view_order(order, current_user.id, current_user.role.value):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order")

    return order