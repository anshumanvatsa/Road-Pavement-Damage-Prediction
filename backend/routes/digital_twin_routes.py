"""Digital twin routes - virtual representations of road segments."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from database import get_db
from models import RoadModel
from services.digital_twin_service import create_digital_twin

router = APIRouter(prefix="/digital-twin", tags=["digital-twin"])


@router.get("/{road_id}", response_model=dict)
async def get_digital_twin(road_id: str, db=Depends(get_db)):
    """
    GET /digital-twin/{road_id}
    Returns DigitalTwin for road - currentCondition, predictedCondition, riskLevel, recommendation.
    Matches frontend structure exactly.
    """
    result = await db.execute(select(RoadModel).where(RoadModel.id == road_id))
    road = result.scalar_one_or_none()
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")

    twin = create_digital_twin(road)
    return twin


@router.get("", response_model=list[dict])
async def get_all_digital_twins(db=Depends(get_db)):
    """
    GET /digital-twin
    Returns all digital twins for all roads.
    """
    result = await db.execute(select(RoadModel).order_by(RoadModel.id))
    roads = result.scalars().all()
    return [create_digital_twin(r) for r in roads]
