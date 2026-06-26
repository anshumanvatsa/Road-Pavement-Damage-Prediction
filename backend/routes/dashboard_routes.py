"""Dashboard routes - aggregate statistics."""
from fastapi import APIRouter, Depends
from sqlalchemy import select

from database import get_db
from models import RoadModel
from services.digital_twin_service import create_digital_twin

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=dict)
async def get_dashboard_stats(db=Depends(get_db)):
    """
    GET /dashboard/stats
    Returns dashboard statistics - total, high, medium, low, avgCondition.
    """
    result = await db.execute(select(RoadModel).order_by(RoadModel.id))
    roads = result.scalars().all()

    twins = [create_digital_twin(r) for r in roads]

    total = len(roads)
    high = sum(1 for t in twins if t["risk_level"] == "High")
    medium = sum(1 for t in twins if t["risk_level"] == "Medium")
    low = sum(1 for t in twins if t["risk_level"] == "Low")

    avg_condition = (
        round(sum(float(r.current_condition_index) for r in roads) / total * 10) / 10
        if total > 0
        else 0
    )

    return {
        "total": total,
        "high": high,
        "medium": medium,
        "low": low,
        "avgCondition": avg_condition,
    }
