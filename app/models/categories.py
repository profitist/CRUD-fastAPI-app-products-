from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import List

from app.database import Base


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey('categories.id'),
        nullable=True
    )

    products: Mapped[List['Product']] = relationship(
        'Product',
        back_populates='category'
    )

    parent: Mapped['Category'] = relationship(
        'Category',
        back_populates='children',
        remote_side='Category.id',
    )

    children: Mapped[List['Category']] = relationship(
        'Category',
        back_populates='parent',
    )
