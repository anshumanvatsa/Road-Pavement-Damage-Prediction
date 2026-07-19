"""FastAPI application - debug wrapper to expose import errors on Vercel."""
import traceback as _tb
import sys

_IMPORT_ERROR: str | None = None

try:
    from contextlib import asynccontextmanager
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from config import get_settings

    # Import routes one by one so we can pinpoint failures
    from routes.road_routes import router as roads_router
    from routes.prediction_routes import router as predictions_router
    from routes.digital_twin_routes import router as digital_twin_router
    from routes.dashboard_routes import router as dashboard_router
    from database import init_db

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Startup: create DB tables and seed if empty. Shutdown: cleanup."""
        try:
            await init_db()
        except Exception as e:
            print(f"init_db warning: {e}")
        try:
            from seed_data import seed_if_empty
            await seed_if_empty()
        except Exception as e:
            print(f"Seed warning: {e}")
        yield

    app = FastAPI(
        title="Predictive Project API",
        description="Backend for climate-aware road degradation monitoring",
        version="1.0.0",
        lifespan=lifespan,
    )

    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from fastapi.responses import JSONResponse

    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "traceback": _tb.format_exc()}
        )

    from fastapi import APIRouter

    api_router = APIRouter(prefix="/api")
    api_router.include_router(roads_router)
    api_router.include_router(predictions_router)
    api_router.include_router(digital_twin_router)
    api_router.include_router(dashboard_router)
    app.include_router(api_router)

except Exception:
    _IMPORT_ERROR = _tb.format_exc()
    # Create a minimal app so Vercel can at least respond
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    app = FastAPI()

    @app.get("/api/health")
    async def health_err():
        return JSONResponse(status_code=500, content={"status": "import_error", "traceback": _IMPORT_ERROR})

    @app.post("/api/predict/custom")
    async def predict_err():
        return JSONResponse(status_code=500, content={"status": "import_error", "traceback": _IMPORT_ERROR})

    @app.post("/api/roads")
    async def roads_err():
        return JSONResponse(status_code=500, content={"status": "import_error", "traceback": _IMPORT_ERROR})

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def catch_all(path: str):
        return JSONResponse(status_code=500, content={"status": "import_error", "traceback": _IMPORT_ERROR})


if _IMPORT_ERROR is None:
    @app.get("/api/health")
    async def health():
        return {"status": "ok", "python": sys.version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
