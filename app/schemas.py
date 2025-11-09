from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, EmailStr, PositiveInt
from typing import Optional, List


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
        description='Название категории (3-50 символов)'
    )
    parent_id: Optional[int] = Field(
        None,
        description='ID родительской категории, если есть'
    )


class Category(BaseModel):
    id: int = Field(
        'Уникальный идентификатор категории'
    )
    name: str = Field(
       description='Название категории'
    )
    parent_id: Optional[int] = Field(
        None,
        description='ID родительской категории'
    )
    is_active: bool = Field(
        Field(description='Активность категории')
    )

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100,
        description='Название товара (3-100 символов)'
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description='Описание товара (до 500 символов)'
    )
    price: float = Field(
        gt=0,
        description='Цена товара (больше 0)'
    )
    image_url: Optional[str] = Field(
        None,
        max_length=200,
        description='URL изображения'
    )
    stock: int = Field(
        ge=0,
        description="Количество товара на складе (0 или больше)"
    )
    category_id: int = Field(
        description="ID категории, к которой относится товар"
    )


class ProductSheme(BaseModel):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: int = Field(description="Уникальный идентификатор товара")
    name: str = Field(description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    price: float = Field(description="Цена товара")
    image_url: Optional[str] = Field(None, description="URL изображения товара")
    stock: int = Field(description="Количество товара на складе")
    category_id: int = Field(description="ID категории")
    is_active: bool = Field(description="Активность товара")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str = Field(description='Email пользователя')
    password: str = Field(
        min_length=8,
        description='Пароль (минимум 8 символов'
    )
    role: str = Field(
        default='buyer',
        pattern='^(buyer|seller|admin)$',
        description='Роль: buyer, seller'
    )


class User(BaseModel):
    id: int
    email: EmailStr = Field(description='Email')
    is_active: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    product_id: int = Field(
        ge=0,
        description='Id товара'
    )
    comment: str = Field(
        default=None,
        description='Отзыв'
    )
    grade: int = Field(
        ge=1,
        le=5,
        description='Оценка пользователя (от 1 до 5)'
    )
    comment_date: datetime = Field(
        ...,
        description='Дата и время комментария'
    )


class Review(BaseModel):
    id: int = Field(..., ge=0)
    user_id: int = Field(..., ge=0)
    product_id: int = Field(..., ge=0)
    comment: str = Field(default=None)
    grade: int = Field(..., ge=1, le=5)
    is_active: bool = Field(default=True)

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    items: List[ProductCreate] = Field(description='Товары для текущей страницы')
    total: int = Field(ge=0, description='Общее количество товаров')
    page: int = Field(ge=1, description='Номер текущей страницы')
    page_size: int = Field(ge=1, description='Количество элементов на странице')

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True, extra='allow')


class OrderList(BaseModel):
    items: List[Order] = Field(description='Список заказов')
    total: int = Field(ge=0, description='Общее количество заказов')
    page: int = Field(ge=1, description='Номер страницы')
    page_size: int = Field(ge=1, description='Количество элементов на странице')

    model_config = ConfigDict(from_attributes=True)
