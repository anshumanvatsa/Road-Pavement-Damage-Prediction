"""Prediction module for road degradation."""
import pickle
from pathlib import Path

import numpy as np


FEATURE_ORDER = [
    "traffic_volume",
    "heavy_vehicle_percentage",
    "rainfall",
    "temperature",
    "humidity",
    "condition",
]


def predict_road_degradation(features: dict) -> float:
    """
    Predict road degradation from features.
    Features: traffic_volume, heavy_vehicle_percentage, rainfall, temperature, humidity, condition
    """
    model_path = Path(__file__).resolve().parent / "model.pkl"
    if not model_path.exists():
        return _rule_based_fallback(features)

    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        X = np.array(
            [[features.get(k, 0) for k in FEATURE_ORDER]],
            dtype=np.float64,
        )
        pred = model.predict(X)
        return float(pred[0])
    except Exception:
        return _rule_based_fallback(features)


def _rule_based_fallback(features: dict) -> float:
    """Fallback using digital-twin formula when model unavailable."""
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
