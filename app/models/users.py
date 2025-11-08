from typing import List
from sqlalchemy import String, DECIMAL
from sqlalchemy.orm import relationship, Mapped, mapped_column


from app.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    role: Mapped[str] = mapped_column(String, default='buyer')

    products: Mapped['ProductModel'] = relationship(
        'ProductModel',
        back_populates='seller'
    )

    reviews: Mapped[List['Review']] = relationship(
        'Review',
        back_populates='user'
    )
