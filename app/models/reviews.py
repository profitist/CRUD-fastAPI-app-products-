from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    comment: Mapped[str] = mapped_column(String, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(), nullable=False
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="reviews")

    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
