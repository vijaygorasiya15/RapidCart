from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from sqlalchemy.orm import Session


def create_product(db: Session, product_in: ProductCreate, seller_id: int) -> Product:
    product = Product(**product_in.model_dump(), seller_id=seller_id)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_all_products(db: Session) -> list[Product]:
    return db.query(Product).all()


def update_product(
    db: Session, product: Product, product_in: ProductUpdate, current_user_id: int
) -> Product:
    if product.seller_id != current_user_id:
        raise PermissionError("You can only update your own products")

    update_data = product_in.model_dump(exclude_unset=True)
    """
    exclude_unset=True in update_product — only fields the client actually sent get updated; 
    fields left out of the request body are left untouched, rather than being overwritten with None.
    """
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product: Product, current_user_id: int) -> None:
    if product.seller_id != current_user_id:
        raise PermissionError("You can only delete your own products")

    db.delete(product)
    db.commit()