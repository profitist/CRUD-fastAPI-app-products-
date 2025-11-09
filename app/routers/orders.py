from typing import List

from fastapi import APIRouter, Depends, Query, HTTPException, status as status_code
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db
from app.models.order import Order as OrderModel
from app.schemas import Order as OrderSchema


router = APIRouter(prefix='orders')


@router.get("/", response_model=List[OrderSchema])
async def get_orders(
        db: AsyncSession = Depends(get_async_db),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        status: str | None = Query(
            None,
            regex="^(paid|in process|canceled)$"

        ),
        min_price: float | None = Query(None, gt=0),
        max_price: float | None = Query(None, gt=0),
):

    if max_price is not None and min_price is not None and max_price < max_price:
        raise HTTPException(
            status_code=status_code.HTTP_400_BAD_REQUEST,
            detail=f"max_price={max_price} min_price={min_price}"
                   f"max price can't be less than min_price={min_price}"
        )

    filters = [OrderModel.is_active == True]
    if status is not None:
        filters.append(OrderModel.status == status)

    if min_price is not None:
        filters.append(OrderModel.total_price >= min_price)
    if max_price is not None:
        filters.append(OrderModel.total_price <= max_price)

    total_stmt = select(
        func.count()
    ).select_from(OrderModel).where(*filters)
    total = await db.scalar(total_stmt)

    order_stmt = select(OrderModel).where(
        *filters
    ).order_by(OrderModel.id).offset((page - 1) * page_size).limit(page_size)
    response = await db.scalars(order_stmt)
    return {
        'items': response.all(),
        'total': total,
        'page': page,
        'page_size': page_size,
    }

