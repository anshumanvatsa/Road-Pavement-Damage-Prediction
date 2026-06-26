"""Services package."""
from services.digital_twin_service import (
    create_digital_twin,
    generate_predictions,
    get_risk_level,
    get_recommendation,
)
from services.prediction_service import predict_road_degradation, get_predictions_for_road
