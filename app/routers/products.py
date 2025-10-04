from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from typing import List, Annotated

from starlette import status

from app.schemas import ProductSheme, ProductCreate, Review
from app.models.products import Product
from app.models.categories import Category
from app.db_depends import get_async_db
from app.models.users import User as UserModel
from app.models.reviews import Review as ReviewModel
from app.auth import get_current_seller

router = APIRouter(
    prefix='/products',
    tags=["products"],
)


@router.get(
    path='/',
    response_model=List[ProductSheme],
    status_code=status.HTTP_200_OK
)
async def get_all_products(db: Annotated[AsyncSession, Depends(get_async_db)]):
    stmt = select(Product).where(Product.is_active)
    response = await db.scalars(stmt)
    return response.all()


@router.post(
    '/', response_model=ProductSheme, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductCreate,
        db: Annotated[AsyncSession, Depends(get_async_db)],
        current_user: Annotated[UserModel, Depends(get_current_seller)]
):
    stmt = select(Category).where(product.category_id == Category.id)
    result = await db.scalars(stmt)
    if result.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {product.category_id} does not exist"
        )
    db_product = Product(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get(
    path='/categories/{category_id}',
    response_model=List[ProductSheme],
    status_code=status.HTTP_200_OK)
async def get_products_category(
        category_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]):
    stmt = select(Product).where(
        and_(
            Product.category_id == category_id,
            Product.is_active
        )
    )
    result = await db.scalars(stmt)
    return result.all()


@router.get(
    path='/{product_id}',
    response_model=ProductSheme,
    status_code=status.HTTP_200_OK
)
async def get_product(
        product_id: int,
        db: Annotated[AsyncSession, Depends(get_async_db)]
):
    stmt = select(Product).where(
        and_(
            product_id == Product.id,
            Product.is_active
        )
    )
    response = await db.scalars(stmt)
    result = response.first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} does not exist"
        )
    return result


@router.put(
    path='/{product_id}',
    response_model=ProductSheme,
    status_code=status.HTTP_200_OK
)
async def update_product(
        product_id: int,
        product: ProductCreate,
        db: Annotated[AsyncSession, Depends(get_async_db)],
        current_user: Annotated[UserModel, Depends(get_current_seller)]
):
    stmt = select(Product).where(product_id == Product.id)
    result = await db.scalars(stmt)
    db_product = result.first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} does not exist"
        )
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can only update your own products")
    stmt = select(Category).where(product.category_id == Category.id)
    result = await db.scalars(stmt)
    if result.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {product.category_id} does not exist"
        )
    await db.execute(
        update(Product).where(
            product_id == Product.id
        ).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(result)
    return result


@router.delete(
    path='/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
        product_id: int,
        db: Annotated[AsyncSession, Depends(get_async_db)],
        current_user: Annotated[UserModel, Depends(get_current_seller)]
):
    stmt = select(Product).where(product_id == Product.id)
    response = await db.scalars(stmt)
    result = response.first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} does not exist"
        )
    result.is_active = False
    await db.commit()


@router.get(
    path='/{product_id}/reviews',
    response_model=List[Review],
    status_code=status.HTTP_200_OK
)
async def get_reviews(
        product_id: int,
        db: Annotated[AsyncSession, Depends(get_async_db)]
):
    response = await db.scalars(
        select(ReviewModel).join(
            Product, ReviewModel.product_id == Product.id
        ).where(
            and_(
                product_id == ReviewModel.product_id,
                ReviewModel.is_active,
                Product.is_active
            )
        )
    )
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} does not exist"
        )
    reviews = response.all()
    return reviews
