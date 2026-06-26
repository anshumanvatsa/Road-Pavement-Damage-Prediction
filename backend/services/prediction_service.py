"""Prediction service - integrates ML model with digital twin logic."""
import os
from pathlib import Path

from models import RoadModel
from services.digital_twin_service import (
    create_digital_twin,
    generate_predictions,
    get_risk_level,
    get_recommendation,
)


def _get_ml_model_path() -> Path:
    """Get path to ML model - relative to backend root."""
    backend_dir = Path(__file__).resolve().parent.parent
    return backend_dir / "ml" / "model.pkl"


def predict_road_degradation(features: dict) -> float:
    """
    Predict degradation using ML model.
    Features: traffic_volume, heavy_vehicle_percentage, rainfall, temperature, humidity, condition
    """
    model_path = _get_ml_model_path()
    if not model_path.exists():
        # Fallback to rule-based if model not trained
        return _rule_based_degradation(features)

    try:
        import pickle
        import numpy as np

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        # Feature order must match training
        feature_order = [
            "traffic_volume",
            "heavy_vehicle_percentage",
            "rainfall",
            "temperature",
            "humidity",
            "condition",
        ]
        X = np.array(
            [[features.get(k, 0) for k in feature_order]],
            dtype=np.float64,
        )
        pred = model.predict(X)
        return float(pred[0])
    except Exception:
        return _rule_based_degradation(features)


def _rule_based_degradation(features: dict) -> float:
    """Fallback degradation using same formula as digital-twin.ts."""
    traffic = features.get("traffic_volume", 0)
    heavy = features.get("heavy_vehicle_percentage", 0)
    rainfall = features.get("rainfall", 0)
    temp = features.get("temperature", 20)
    humidity = features.get("humidity", 50)
    condition = features.get("condition", 75)

    traffic_factor = (traffic / 10000) * 2
    heavy_factor = (heavy / 100) * 5
    rainfall_factor = (rainfall / 300) * 3
    temp_factor = abs(temp - 20) / 20 * 2
    humidity_factor = (humidity / 100) * 1.5

    base = traffic_factor + heavy_factor + rainfall_factor + temp_factor + humidity_factor
    multiplier = 1 + (100 - condition) / 100
    return round(base * multiplier * 100) / 100


def get_predictions_for_road(road: RoadModel, use_ml: bool = True) -> list[dict]:
    """Get predictions for road - optionally enhanced with ML degradation."""
    if use_ml:
        return _ml_enhanced_predictions(road)
    return generate_predictions(road)


def _ml_enhanced_predictions(road: RoadModel) -> list[dict]:
    """Generate predictions using ML model for degradation."""
    from datetime import date, timedelta

    model_path = _get_ml_model_path()
    condition = float(road.current_condition_index)
    predictions = []

    features = {
        "traffic_volume": float(road.traffic_volume),
        "heavy_vehicle_percentage": float(road.heavy_vehicle_percentage),
        "rainfall": float(road.rainfall),
        "temperature": float(road.temperature),
        "humidity": float(road.humidity),
    }

    for month in range(1, 7):
        features["condition"] = condition
        base_degradation = predict_road_degradation(features)
        degradation = base_degradation * (month * 0.15)
        condition = max(0, condition - degradation * 0.5)

        pred_date = date.today() + timedelta(days=month * 30)

        predictions.append(
            {
                "id": f"pred-{road.id}-{month}",
                "road_segment_id": road.id,
                "predicted_condition_index": round(condition * 10) / 10,
                "predicted_degradation": round(degradation * 100) / 100,
                "risk_level": get_risk_level(degradation),
                "prediction_date": pred_date.isoformat(),
                "month_offset": month,
            }
        )

    return predictions
