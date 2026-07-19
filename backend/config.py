"""Application configuration."""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


import shutil

class Settings:
    """Application settings loaded from environment."""

    _base_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictive.db")
    _db_path = _base_db_path
    
    # In Vercel serverless, the filesystem is read-only except for /tmp.
    if os.getenv("VERCEL") == "1":
        _db_path = "/tmp/predictive.db"
        if not os.path.exists(_db_path) and os.path.exists(_base_db_path):
            shutil.copy2(_base_db_path, _db_path)

    database_url: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{_db_path.replace(os.sep, '/')}" if os.getenv("USE_SQLITE", "0") == "1" else "postgresql+asyncpg://postgres:postgres@localhost:5432/predictive_db",
    )
    database_url_sync: str = os.getenv(
        "DATABASE_URL_SYNC",
        f"sqlite:///{_db_path.replace(os.sep, '/')}" if os.getenv("USE_SQLITE", "0") == "1" else "postgresql://postgres:postgres@localhost:5432/predictive_db",
    )

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ]

    # ML
    ml_model_path: str = os.getenv("ML_MODEL_PATH", "ml/model.pkl")


@lru_cache
def get_settings() -> Settings:
    return Settings()
