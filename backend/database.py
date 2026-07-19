"""Database connection and session management."""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

settings = get_settings()

# SQLite (aiosqlite / NullPool) does NOT support pool_size or max_overflow.
_is_sqlite = settings.database_url.startswith("sqlite")

engine_kwargs: dict = {
    "echo": False,
}
if not _is_sqlite:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(settings.database_url, **engine_kwargs)

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
    Ensures DB tables exist on the very first request (Vercel serverless
    skips FastAPI lifespan events, so we guard here).
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
    """Create all database tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
