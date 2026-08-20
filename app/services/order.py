from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate
from sqlalchemy.orm import Session, joinedload

ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED},
    OrderStatus.DELIVERED: set(),
    OrderStatus.CANCELLED: set(),
}


def is_valid_transition(current: OrderStatus, new: OrderStatus) -> bool:
    return new in ALLOWED_TRANSITIONS.get(current, set())
"""
Get the value for current. If current does not exist as a key, return an empty set instead.
set() here is a fallback/default value.
"""

def update_order_status(
    db: Session,
    order: Order,
    new_status: OrderStatus,
    current_user_id: int,
    role: str,
) -> Order:
    if role == "admin":
        pass  # admin can override any transition, including otherwise-illegal ones
    elif role == "seller":
        is_seller_of_order = any(item.product.seller_id == current_user_id for item in order.items)
        if not is_seller_of_order:
            raise PermissionError("You can only update orders containing your products")
        if not is_valid_transition(order.status, new_status):
            raise ValueError(f"Cannot transition from {order.status.value} to {new_status.value}")
    elif role == "buyer":
        if order.buyer_id != current_user_id:
            raise PermissionError("You can only cancel your own orders")
        if new_status != OrderStatus.CANCELLED:
            raise PermissionError("Buyers can only cancel orders")
        if order.status not in {OrderStatus.PENDING, OrderStatus.CONFIRMED}:
            raise ValueError("Only pending or confirmed orders can be cancelled")
    else:
        raise PermissionError("Not authorized to update order status")

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order

def create_order(db: Session, order_in: OrderCreate, buyer_id: int) -> Order:
    if not order_in.items:
        raise ValueError("Order must contain at least one item")

    order_items = []
    total = 0.0

    for item in order_in.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"Product {item.product_id} not found")
        if product.stock < item.quantity:
            raise ValueError(
                f"Insufficient stock for '{product.name}' (available: {product.stock})"
            )

        product.stock -= item.quantity
        line_total = product.price * item.quantity
        total += line_total

        order_items.append(
            OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                price_at_purchase=product.price,
            )
        )

    order = Order(buyer_id=buyer_id, total=total, items=order_items)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order_by_id(db: Session, order_id: int) -> Order | None:
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )


def get_buyer_orders(db: Session, buyer_id: int) -> list[Order]:
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.buyer_id == buyer_id)
        .all()
    )


def get_seller_orders(db: Session, seller_id: int) -> list[Order]:
    return (
        db.query(Order)
        .join(OrderItem, Order.id == OrderItem.order_id)
        .join(Product, OrderItem.product_id == Product.id)
        .filter(Product.seller_id == seller_id)
        .options(joinedload(Order.items))
        .distinct()
        .all()
    )


def user_can_view_order(order: Order, user_id: int, role: str) -> bool:
    if role == "admin":
        return True
    if order.buyer_id == user_id:
        return True
    return any(item.product.seller_id == user_id for item in order.items)