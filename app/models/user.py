import enum
from datetime import datetime, timezone

from app.db.database import Base
from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship


class RoleEnum(str, enum.Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.BUYER)
    created_at = Column(DateTime(timezone=True), default= lambda: datetime.now(timezone.utc))

    # back_populates keeps both sides of a relationship connected and synchronized in the ORM.
    products = relationship("Product", back_populates="seller")
    # orders = relationship("Order", back_populates="buyer")

