from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate
from sqlalchemy.orm import Session, joinedload


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