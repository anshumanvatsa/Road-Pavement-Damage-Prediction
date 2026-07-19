"""Database connection and session management."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


_db_initialized = False

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides a database session.
    Also ensures DB is initialized on first request for serverless environments
    that skip FastAPI lifespan events.
    """
    global _db_initialized
    if not _db_initialized:
        await init_db()
        try:
            from seed_data import seed_if_empty
            await seed_if_empty()
        except Exception as e:
            print(f"Seed warning: {e}")
        _db_initialized = True

    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
