from fastapi import APIRouter, Depends, status, HTTPException
from typing import List, Annotated, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas import Review, ReviewCreate
from app.db_depends import get_async_db
from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.models.products import Product as ProductModel
from app.auth import get_current_buyer, get_current_admin

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


@router.get(path="/", response_model=List[Review], status_code=status.HTTP_200_OK)
async def get_reviews(
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> List[ReviewModel]:
    stmt = select(ReviewModel).where(ReviewModel.is_active)
    response = await db.scalars(stmt)
    db_reviews = response.all()
    return db_reviews


@router.post(path="/", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_review(
    review: ReviewCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[UserModel, Depends(get_current_buyer)],
) -> Review:
    user_id = current_user.id

    stmt = select(Product).where(review.product_id == Product.id, Product.is_active)

    db_response = await db.scalars(stmt)
    db_product = db_response.first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product does not exist"
        )

    db_review = ReviewModel(**review.model_dump(), user_id=user_id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    await update_product_rating(db, product_id=db_product.id)
    return db_review


async def update_product_rating(db: AsyncSession, product_id: int) -> None:
    result = await db.execute(
        select(func.avg(ReviewModel.grade)).where(
            product_id == ReviewModel.product_id, ReviewModel.is_active
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(Product, product_id)
    product.rating = avg_rating
    await db.commit()


# @router.delete(
#     path='/{review_id}',
#     response_model=Dict[str, str],
#     status_code=status.HTTP_200_OK
# )
# async def delete_review(
#         db: Annotated[AsyncSession, Depends(get_async_db)],
#         review_id: int,
#         auth: Annotated[UserModel, Depends(get_current_admin)]
# ) -> Dict:
#     stmt = select(ReviewModel).where(review_id == ReviewModel.id)
#     db_response = await db.scalars(stmt)
#     db_review = db_response.first()
#     if not db_review:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Review does not exist"
#         )
#     db_review.is_active = False
#     await db.commit()
#     await db.refresh(db_review)
#     return {'message': 'Review deleted'}
