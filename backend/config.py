"""Application configuration - Vercel-compatible, zero pydantic-settings dependency."""
import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

# Detect serverless / Vercel environment
_IS_VERCEL = os.getenv("VERCEL") == "1" or os.getenv("USE_SQLITE") == "1"

# On Vercel the only writable directory is /tmp.
# We copy the bundled DB there once so migrations can run.
if _IS_VERCEL:
    import shutil
    _src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictive.db")
    _dst = "/tmp/predictive.db"
    if not os.path.exists(_dst) and os.path.exists(_src):
        try:
            shutil.copy2(_src, _dst)
        except Exception:
            pass  # will create fresh DB below
    _db_file = _dst
else:
    _db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictive.db")

# Always use forward slashes for SQLite URL (Windows compat)
_db_url_async = f"sqlite+aiosqlite:///{_db_file.replace(os.sep, '/')}"
_db_url_sync  = f"sqlite:///{_db_file.replace(os.sep, '/')}"


class Settings:
    """Application settings."""

    database_url: str = os.getenv("DATABASE_URL", _db_url_async)
    database_url_sync: str = os.getenv("DATABASE_URL_SYNC", _db_url_sync)

    # CORS – allow everything; tighten after demo
    cors_origins: list = ["*"]

    # ML
    ml_model_path: str = os.getenv("ML_MODEL_PATH", "ml/model.pkl")


@lru_cache
def get_settings() -> Settings:
    return Settings()
