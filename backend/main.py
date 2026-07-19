"""FastAPI application - production-grade backend for Predictive Project."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_db
from routes.road_routes import router as roads_router
from routes.prediction_routes import router as predictions_router
from routes.digital_twin_routes import router as digital_twin_router
from routes.dashboard_routes import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables and seed if empty. Shutdown: cleanup."""
    await init_db()
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
    allow_origins=["*"], # allow all for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "traceback": traceback.format_exc()}
    )

from fastapi import APIRouter

api_router = APIRouter(prefix="/api")
api_router.include_router(roads_router)
api_router.include_router(predictions_router)
api_router.include_router(digital_twin_router)
api_router.include_router(dashboard_router)

app.include_router(api_router)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
