"""Road routes - CRUD for road segments."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import PredictionModel, RoadModel
from schemas import RoadSegmentCreate
from services.prediction_service import get_predictions_for_road

router = APIRouter(prefix="/roads", tags=["roads"])


def _road_to_schema(road: RoadModel) -> dict:
    """Convert RoadModel to frontend-compatible dict."""
    return {
        "id": road.id,
        "road_name": road.road_name,
        "location": road.location,
        "latitude": float(road.latitude),
        "longitude": float(road.longitude),
        "current_condition_index": float(road.current_condition_index),
        "traffic_volume": int(road.traffic_volume),
        "heavy_vehicle_percentage": float(road.heavy_vehicle_percentage),
        "rainfall": float(road.rainfall),
        "temperature": float(road.temperature),
        "humidity": float(road.humidity),
        "last_updated": road.last_updated,
    }


@router.get("", response_model=list[dict])
async def get_roads(db: AsyncSession = Depends(get_db)):
    """
    GET /roads
    Returns list of RoadSegment - matches frontend structure exactly.
    """
    result = await db.execute(select(RoadModel).order_by(RoadModel.id))
    roads = result.scalars().all()
    return [_road_to_schema(r) for r in roads]


@router.get("/{road_id}/predictions", response_model=list[dict])
async def get_road_predictions(road_id: str, db: AsyncSession = Depends(get_db)):
    """
    GET /roads/{road_id}/predictions
    Returns predictions for road - matches frontend Prediction[] format.
    """
    result = await db.execute(select(RoadModel).where(RoadModel.id == road_id))
    road = result.scalar_one_or_none()
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")

    pred_result = await db.execute(
        select(PredictionModel)
        .where(PredictionModel.road_segment_id == road_id)
        .order_by(PredictionModel.month_offset)
    )
    stored = pred_result.scalars().all()

    if stored:
        return [
            {
                "id": p.id,
                "road_segment_id": p.road_segment_id,
                "predicted_condition_index": float(p.predicted_condition_index),
                "predicted_degradation": float(p.predicted_degradation),
                "risk_level": p.risk_level,
                "prediction_date": p.prediction_date,
                "month_offset": p.month_offset,
            }
            for p in stored
        ]

    predictions_data = get_predictions_for_road(road)
    return predictions_data


@router.get("/{road_id}", response_model=dict)
async def get_road(road_id: str, db: AsyncSession = Depends(get_db)):
    """
    GET /roads/{id}
    Returns single RoadSegment.
    """
    result = await db.execute(select(RoadModel).where(RoadModel.id == road_id))
    road = result.scalar_one_or_none()
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")
    return _road_to_schema(road)


@router.post("", response_model=dict, status_code=201)
async def create_road(body: RoadSegmentCreate, db: AsyncSession = Depends(get_db)):
    """
    POST /roads
    Create new road segment. Returns RoadSegment with id and last_updated.
    """
    # Generate next id
    count_result = await db.execute(select(func.count()).select_from(RoadModel))
    count = count_result.scalar() or 0
    new_id = f"road-{str(count + 1).zfill(3)}"

    road = RoadModel(
        id=new_id,
        road_name=body.road_name,
        location=body.location,
        latitude=body.latitude,
        longitude=body.longitude,
        current_condition_index=body.current_condition_index,
        traffic_volume=body.traffic_volume,
        heavy_vehicle_percentage=body.heavy_vehicle_percentage,
        rainfall=body.rainfall,
        temperature=body.temperature,
        humidity=body.humidity,
        last_updated=date.today().isoformat(),
    )
    db.add(road)
    await db.flush()
    await db.refresh(road)
    return _road_to_schema(road)
