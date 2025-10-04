from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, and_
from sqlalchemy.orm import Session
from typing import Annotated, List

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_db

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


@router.get(
    "/", response_model=List[CategorySchema],
    status_code=status.HTTP_200_OK
)
async def get_all_categories(
        db: Annotated[AsyncSession, Depends(get_async_db)]
):
    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.is_active))
    categories = result.all()
    return categories


@router.post(
    path="/",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
        category: CategoryCreate,
        db: AsyncSession = Depends(get_async_db)
):
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(
            category.parent_id == CategoryModel.id)
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(
                status_code=400,
                detail="Parent category not found"
            )

    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.put(
    "/{category_id}",
    response_model=CategorySchema,
    status_code=status.HTTP_200_OK)
async def update_category(
        category_id: int,
        category: CategoryCreate,
        db: Annotated[AsyncSession, Depends(get_async_db)]):
    stmt = select(CategoryModel).where(
        and_(CategoryModel.id == category_id, CategoryModel.is_active))
    result = await db.scalars(stmt)
    db_category = result.first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category does not exist'
    )

    if category.parent_id is not None:
        stmt = select(CategoryModel).where(
            category.parent_id == CategoryModel.id)
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Parent category does not exist'
            )

        await db.execute(
            update(CategoryModel).where(
                category_id == CategoryModel.id,
            ).values(**category.model_dump())
        )
        await db.commit()
        await db.refresh(db_category)
        return db_category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]):
    stmt = select(CategoryModel).where(
        and_(CategoryModel.id == category_id, CategoryModel.is_active))
    result = await db.scalars(stmt)
    category = result.first()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category does not exist or already not active'
        )
    await db.execute(update(CategoryModel).where(
        category_id == CategoryModel.id).values(is_active=False))
    await db.commit()
    return {"status": "success", "message": "Category marked as inactive"}
