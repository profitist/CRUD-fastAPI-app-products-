from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import dotenv_values
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite:///ecommerce.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


secrets = dotenv_values(".env")

# Строка подключения для SQLite
DATABASE_URL = (
    f"postgresql+asyncpg://{secrets['POSTGRES_USER']}:"
    f"{secrets['POSTGRES_PASSWORD']}@db:5432/ecommerce_db"
)

# Создаём Engine
async_engine = create_async_engine(DATABASE_URL, echo=True)

# Настраиваем фабрику сеансов
async_session_maker = async_sessionmaker(
    async_engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass
