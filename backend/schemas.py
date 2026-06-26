"""Pydantic schemas matching frontend types exactly."""
from pydantic import BaseModel, Field


# Risk level - must match frontend: 'Low' | 'Medium' | 'High'
RiskLevel = str  # Literal["Low", "Medium", "High"]


class RoadSegmentBase(BaseModel):
    """Base schema for road segment - matches frontend RoadSegment (create)."""
    road_name: str
    location: str
    latitude: float
    longitude: float
    current_condition_index: float
    traffic_volume: int
    heavy_vehicle_percentage: float
    rainfall: float
    temperature: float
    humidity: float


class RoadSegmentCreate(RoadSegmentBase):
    """Schema for creating a road - omit id and last_updated."""
    pass


class RoadSegment(RoadSegmentBase):
    """Full RoadSegment - matches frontend types.ts exactly."""
    id: str
    last_updated: str

    model_config = {"from_attributes": True}


class Prediction(BaseModel):
    """Prediction schema - matches frontend types.ts exactly."""
    id: str
    road_segment_id: str
    predicted_condition_index: float
    predicted_degradation: float
    risk_level: RiskLevel
    prediction_date: str
    month_offset: int

    model_config = {"from_attributes": True}


class DigitalTwin(BaseModel):
    """DigitalTwin schema - matches frontend types.ts exactly."""
    id: str
    road_segment_id: str
    current_state: float
    predicted_state: float
    risk_level: RiskLevel
    maintenance_recommendation: str

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total: int
    high: int
    medium: int
    low: int
    avgCondition: float
