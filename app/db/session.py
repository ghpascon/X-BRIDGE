from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from sqlalchemy import create_engine

async_driver = settings.DATABASE_URL.split('+')[1].split(':')[0]
sync_url = settings.DATABASE_URL.replace(f"+{async_driver}", "+pymysql")

sync_engine = create_engine(sync_url, echo=False)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autocommit=False
)

Base = declarative_base()
