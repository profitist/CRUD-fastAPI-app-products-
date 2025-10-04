import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Annotated, List
from fastapi.security import OAuth2PasswordRequestForm

from app.models.users import User as UserModel
from app.schemas import UserCreate, User as UserSchema, Review as ReviewSchema, \
    Review
from app.db_depends import get_async_db
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    JWT_SECRET_KEY,
    ALGORITHM
)

router = APIRouter(
    prefix='/users',
    tags=['users'],
)


@router.post(
    path='/',
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
        user: UserCreate,
        db: Annotated[AsyncSession, Depends(get_async_db)],
):
    result = await db.scalars(
        select(UserModel).where(user.email == UserModel.email)
    )
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already registered'
        )

    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
    )

    db.add(db_user)
    await db.commit()
    return db_user


@router.post('/token')
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(get_async_db)],
):
    result = await db.scalars(select(UserModel).where(
        form_data.username == UserModel.email)
    )

    user = result.first()

    if not user or not verify_password(
            form_data.password,
            user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    access_token = create_access_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id},
    )
    refresh_token = create_refresh_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id}
    )
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer'
    }


@router.post('/refresh-token')
async def refresh_access_token(
        refresh_token: str,
        db: Annotated[AsyncSession, Depends(get_async_db)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not refresh token',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(
            refresh_token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        email: str = payload.get('sub')
        if email is None:
            raise credentials_exception
    except jwt.exceptions:
        raise credentials_exception
    result = await db.scalars(
        select(UserModel).where(
            and_(
                email == UserModel.email,
                UserModel.is_active
            )
        )
    )
    user = result.first()
    if user is None:
        raise credentials_exception
    access_token = create_access_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id}
    )
    return {'access_token': access_token, 'token_type': 'bearer'}


