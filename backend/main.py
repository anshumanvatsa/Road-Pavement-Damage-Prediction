"""FastAPI application - production-grade backend for Predictive Project."""
import sys
import traceback as _tb
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Track any startup import errors so we can expose them via the health endpoint
_startup_errors: list[str] = []

# ── App must be defined at module top-level so Vercel's static parser finds it ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables and seed if empty."""
    try:
        from database import init_db
        await init_db()
    except Exception as exc:
        _startup_errors.append(f"init_db failed: {exc}\n{_tb.format_exc()}")

    try:
        from seed_data import seed_if_empty
        await seed_if_empty()
    except Exception as exc:
        _startup_errors.append(f"seed failed: {exc}\n{_tb.format_exc()}")

    yield


app = FastAPI(
    title="Predictive Project API",
    description="Backend for climate-aware road degradation monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": _tb.format_exc()},
    )


@app.get("/api/health")
async def health():
    """Health check - also reports any startup import errors."""
    return {
        "status": "ok" if not _startup_errors else "degraded",
        "python": sys.version,
        "startup_errors": _startup_errors,
    }


# ── Routers - imported lazily inside a guard so any error is surfaced clearly ──
try:
    from config import get_settings  # noqa: F401 - validates config can load
    from routes.road_routes import router as roads_router
    from routes.prediction_routes import router as predictions_router
    from routes.digital_twin_routes import router as digital_twin_router
    from routes.dashboard_routes import router as dashboard_router
    from fastapi import APIRouter

    api_router = APIRouter(prefix="/api")
    api_router.include_router(roads_router)
    api_router.include_router(predictions_router)
    api_router.include_router(digital_twin_router)
    api_router.include_router(dashboard_router)
    app.include_router(api_router)

except Exception:
    _err = _tb.format_exc()
    _startup_errors.append(f"Router import failed:\n{_err}")

    # Fallback stubs so the app doesn't return 404 on known API paths
    @app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def api_error_stub(path: str):
        return JSONResponse(
            status_code=500,
            content={"detail": "Backend failed to start", "traceback": _err},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
