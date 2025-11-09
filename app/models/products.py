from typing import List

from sqlalchemy import String, DECIMAL, Boolean, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.database import Base
from app.models.order import order_products

class ProductModel(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rating: Mapped[float] = mapped_column(
        DECIMAL,
        server_default='0.0',
        default=0.0
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id'),
        nullable=False
    )
    seller_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False
    )
    seller: Mapped['Users'] = relationship(
        'User',
        back_populates='products'
    )
    category: Mapped['Category'] = relationship(
        'Category',
        back_populates='products'
    )
    reviews: Mapped['Review'] = relationship(
        'Review',
        back_populates='product'
    )

    orders: Mapped[List['Order']] = relationship(
        'Order',
        secondary=order_products,
        back_populates='items'
    )

