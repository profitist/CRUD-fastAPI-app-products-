from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, update, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth import get_current_seller
from app.db_depends import get_async_db
from app.models.categories import Category
from app.models.products import Product
from app.models.reviews import Review as ReviewModel
from app.models.users import User as UserModel
from app.schemas import ProductSheme, ProductCreate, Review, ProductList

router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get(path="/", response_model=ProductList, status_code=status.HTTP_200_OK)
async def get_all_products(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, gt=0, le=1),
    category_id: int | None = Query(None, description="ID категории"),
    min_price: float | None = Query(None, description="Минимальная цена товара"),
    max_price: float | None = Query(None, description="Максимальная цена товара"),
    search: str | None = Query(
        None, min_length=1, description="Поиск по названию товара"
    ),
    in_stock: bool | None = Query(
        None, description="true - товар есть в наличии, иначе false"
    ),
    seller_id: int | None = Query(None, description="ID продавца для фильтрации"),
):
    if min_price and max_price and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price не может быть больше max_price",
        )

    filters = [Product.is_active == True]
    if category_id is not None:
        filters.append(Product.category_id == category_id)
    if min_price is not None:
        filters.append(Product.price >= min_price)
    if max_price is not None:
        filters.append(Product.price <= max_price)
    if in_stock is not None:
        filters.append(Product.stock > 0 if in_stock else Product.stock == 0)
    if seller_id is not None:
        filters.append(Product.seller == seller_id)

    total_stmt = select(func.count()).select_from(Product).where(*filters)

    rank_col = None
    if search is not None:
        search_value = search.strip()
        if search_value:
            ts_query = func.websearch_to_tsquery("english", search_value)
            filters.append(Product.tsv.op("@@")(ts_query))
            rank_col = func.ts_rank(Product.tsv, ts_query).label("rank")
            total_stmt = select(func.count()).select_from(Product).where(*filters)

    total = await db.scalar(total_stmt) or 0

    if rank_col is not None:
        products_stmt = (
            select(Product, rank_col)
            .where(*filters)
            .order_by(desc(rank_col), Product.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(products_stmt)
        row = result.all()
        items = [row[0] for row in row]
    else:
        products_stmt = (
            select(Product)
            .where(*filters)
            .order_by(Product.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = (await db.scalars(products_stmt)).all()

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/", response_model=ProductSheme, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[UserModel, Depends(get_current_seller)],
):
    stmt = select(Category).where(product.category_id == Category.id)
    result = await db.scalars(stmt)
    if result.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {product.category_id} does not exist",
        )
    db_product = Product(**product.model_dump(), seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@router.get(
    path="/categories/{category_id}",
    response_model=List[ProductSheme],
    status_code=status.HTTP_200_OK,
)
async def get_products_category(
    category_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    stmt = select(Product).where(
        and_(Product.category_id == category_id, Product.is_active)
    )
    result = await db.scalars(stmt)
    return result.all()


@router.get(
    path="/{product_id}", response_model=ProductSheme, status_code=status.HTTP_200_OK
)
async def get_product(
    product_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    stmt = select(Product).where(and_(product_id == Product.id, Product.is_active))
    response = await db.scalars(stmt)
    result = response.first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} does not exist",
        )
    return result


@router.put(
    path="/{product_id}", response_model=ProductSheme, status_code=status.HTTP_200_OK
)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[UserModel, Depends(get_current_seller)],
):
    stmt = select(Product).where(product_id == Product.id)
    result = await db.scalars(stmt)
    db_product = result.first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} does not exist",
        )
    if db_product.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own products",
        )
    stmt = select(Category).where(product.category_id == Category.id)
    result = await db.scalars(stmt)
    if result.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category {product.category_id} does not exist",
        )
    await db.execute(
        update(Product).where(product_id == Product.id).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(result)
    return result


@router.delete(path="/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[UserModel, Depends(get_current_seller)],
):
    stmt = select(Product).where(product_id == Product.id)
    response = await db.scalars(stmt)
    result = response.first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} does not exist",
        )
    result.is_active = False
    await db.commit()


@router.get(
    path="/{product_id}/reviews",
    response_model=List[Review],
    status_code=status.HTTP_200_OK,
)
async def get_reviews(
    product_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    response = await db.scalars(
        select(ReviewModel)
        .join(Product, ReviewModel.product_id == Product.id)
        .where(
            and_(
                product_id == ReviewModel.product_id,
                ReviewModel.is_active,
                Product.is_active,
            )
        )
    )
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_id} does not exist",
        )
    reviews = response.all()
    return reviews
