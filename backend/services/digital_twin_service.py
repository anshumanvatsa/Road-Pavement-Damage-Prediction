"""Digital twin service - logic must match frontend digital-twin.ts exactly."""
from typing import Literal

from models import RoadModel

RiskLevel = Literal["Low", "Medium", "High"]


def calculate_degradation(road: RoadModel) -> float:
    """Calculate degradation - matches frontend calculateDegradation exactly."""
    traffic_factor = (float(road.traffic_volume) / 10000) * 2
    heavy_vehicle_factor = (float(road.heavy_vehicle_percentage) / 100) * 5
    rainfall_factor = (float(road.rainfall) / 300) * 3
    temp_factor = abs(float(road.temperature) - 20) / 20 * 2
    humidity_factor = (float(road.humidity) / 100) * 1.5

    base_degradation = (
        traffic_factor
        + heavy_vehicle_factor
        + rainfall_factor
        + temp_factor
        + humidity_factor
    )
    condition_multiplier = 1 + (100 - float(road.current_condition_index)) / 100

    return round(base_degradation * condition_multiplier * 100) / 100


def get_risk_level(degradation: float) -> RiskLevel:
    """Risk logic: Low < 5, Medium 5-15, High > 15 - matches frontend exactly."""
    if degradation < 5:
        return "Low"
    if degradation <= 15:
        return "Medium"
    return "High"


def get_recommendation(risk: RiskLevel) -> str:
    """Get maintenance recommendation - matches frontend getRecommendation exactly."""
    if risk == "Low":
        return "Monitor — routine inspection sufficient"
    if risk == "Medium":
        return "Schedule preventive maintenance within 30 days"
    return "Immediate repair required — critical degradation detected"


def generate_predictions(road: RoadModel) -> list[dict]:
    """Generate 6-month predictions - matches frontend generatePredictions exactly."""
    import math
    from datetime import date, timedelta

    predictions: list[dict] = []
    condition = float(road.current_condition_index)

    for month in range(1, 7):
        seasonal_factor = 1 + 0.3 * math.sin((month / 12) * math.pi * 2)
        # Create a mock road with updated condition for degradation calc
        mock_condition = condition
        degradation = (
            _calc_degradation_for_condition(
                road,
                mock_condition,
            )
            * seasonal_factor
            * (month * 0.15)
        )
        condition = max(0, condition - degradation * 0.5)

        pred_date = date.today() + timedelta(days=month * 30)
        pred_date_str = pred_date.isoformat()

        predictions.append(
            {
                "id": f"pred-{road.id}-{month}",
                "road_segment_id": road.id,
                "predicted_condition_index": round(condition * 10) / 10,
                "predicted_degradation": round(degradation * 100) / 100,
                "risk_level": get_risk_level(degradation),
                "prediction_date": pred_date_str,
                "month_offset": month,
            }
        )

    return predictions


def _calc_degradation_for_condition(road: RoadModel, condition: float) -> float:
    """Helper to compute degradation for a given condition value."""
    traffic_factor = (float(road.traffic_volume) / 10000) * 2
    heavy_vehicle_factor = (float(road.heavy_vehicle_percentage) / 100) * 5
    rainfall_factor = (float(road.rainfall) / 300) * 3
    temp_factor = abs(float(road.temperature) - 20) / 20 * 2
    humidity_factor = (float(road.humidity) / 100) * 1.5

    base_degradation = (
        traffic_factor
        + heavy_vehicle_factor
        + rainfall_factor
        + temp_factor
        + humidity_factor
    )
    condition_multiplier = 1 + (100 - condition) / 100
    return base_degradation * condition_multiplier


def create_digital_twin(road: RoadModel) -> dict:
    """Create digital twin from road - matches frontend createDigitalTwin exactly."""
    predictions = generate_predictions(road)
    worst = max(predictions, key=lambda p: p["predicted_degradation"])
    risk = worst["risk_level"]

    return {
        "id": f"twin-{road.id}",
        "road_segment_id": road.id,
        "current_state": float(road.current_condition_index),
        "predicted_state": worst["predicted_condition_index"],
        "risk_level": risk,
        "maintenance_recommendation": get_recommendation(risk),
    }
