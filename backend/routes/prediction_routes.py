"""Prediction routes - ML-based road degradation predictions."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select

from database import get_db
from models import RoadModel, PredictionModel
from schemas import Prediction, CustomPredictionRequest
from services.digital_twin_service import generate_predictions, get_risk_level
from services.prediction_service import predict_road_degradation, get_predictions_for_road

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post("/custom", response_model=dict)
async def custom_prediction(req: CustomPredictionRequest):
    """
    POST /predict/custom
    Predict road degradation on the fly for custom map clicks.
    """
    features = {
        "traffic_volume": req.traffic_volume,
        "heavy_vehicle_percentage": req.heavy_vehicle_percentage,
        "rainfall": req.rainfall,
        "temperature": req.temperature,
        "humidity": req.humidity,
        "condition": req.current_condition
    }
    
    degradation = predict_road_degradation(features)
    new_condition = max(0, min(100, req.current_condition - degradation))
    
    if new_condition < 40:
        risk = "High"
    elif new_condition < 70:
        risk = "Medium"
    else:
        risk = "Low"
        
    return {
        "degradation": degradation,
        "new_condition": new_condition,
        "risk_level": risk
    }

@router.post("/{road_id}", response_model=list[dict])
async def run_prediction(
    road_id: str,
    db=Depends(get_db),
    use_ml: bool = Query(True, description="Use ML model if available"),
):
    """
    POST /predict/{road_id}
    Run prediction for road. Returns list of Prediction matching frontend format.
    Stores predictions in database.
    """
    result = await db.execute(select(RoadModel).where(RoadModel.id == road_id))
    road = result.scalar_one_or_none()
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")

    if use_ml:
        predictions_data = get_predictions_for_road(road, use_ml=True)
    else:
        predictions_data = generate_predictions(road)

    # Store predictions in database (upsert - delete old, insert new)
    await db.execute(
        delete(PredictionModel).where(PredictionModel.road_segment_id == road_id)
    )

    for p in predictions_data:
        pred_model = PredictionModel(
            id=p["id"],
            road_segment_id=p["road_segment_id"],
            predicted_condition_index=p["predicted_condition_index"],
            predicted_degradation=p["predicted_degradation"],
            risk_level=p["risk_level"],
            prediction_date=p["prediction_date"],
            month_offset=p["month_offset"],
        )
        db.add(pred_model)

    await db.flush()

    return predictions_data


@router.get("/{road_id}", response_model=list[dict])
async def get_predictions(
    road_id: str,
    db=Depends(get_db),
):
    """
    GET /roads/{road_id}/predictions - alternate path
    Get predictions for road. Generates if none stored.
    """
    result = await db.execute(select(RoadModel).where(RoadModel.id == road_id))
    road = result.scalar_one_or_none()
    if not road:
        raise HTTPException(status_code=404, detail="Road not found")

    # Check if we have stored predictions
    pred_result = await db.execute(
        select(PredictionModel).where(
            PredictionModel.road_segment_id == road_id
        ).order_by(PredictionModel.month_offset)
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

    # Generate on the fly
    predictions_data = get_predictions_for_road(road)
    return predictions_data
