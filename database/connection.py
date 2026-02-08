"""
Database connection dan session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from typing import AsyncGenerator
import os

from app.config import settings

# Async engine untuk PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Sync engine (untuk migrasi) - commented out untuk sekarang
# sync_engine = create_engine(
#     settings.DATABASE_URL.replace("+asyncpg", ""),
#     echo=settings.DEBUG,
#     pool_pre_ping=True
# )

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync session factory (untuk migrasi) - commented out
# SessionLocal = sessionmaker(
#     bind=sync_engine,
#     autocommit=False,
#     autoflush=False
# )


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency untuk mendapatkan async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Sync version - untuk compatibility (gunakan get_async_db untuk production)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency untuk mendapatkan database session (async wrapper)"""
    async for session in get_async_db():
        yield session
