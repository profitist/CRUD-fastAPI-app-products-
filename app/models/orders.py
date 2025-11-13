from typing import List

from sqlalchemy import Integer, ForeignKey, Table, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

order_products = Table(
    "order_products",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "order_id",
        Integer,
        ForeignKey("orders.id"),
        primary_key=True,
        index=True,
    ),
    Column("product_id", Integer, ForeignKey("products.id")),
)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(default="in process")
    total_price: Mapped[float] = mapped_column(default=0.0)
    items: Mapped[List["Product"]] = relationship(
        "Product", back_populates="orders", secondary=order_products
    )
