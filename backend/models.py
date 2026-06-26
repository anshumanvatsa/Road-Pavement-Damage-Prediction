"""SQLAlchemy ORM models matching frontend types."""
from datetime import date
from decimal import Decimal

from sqlalchemy import String, Numeric, Integer, Text, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class RoadModel(Base):
    """Road segment model - matches RoadSegment from frontend types.ts."""

    __tablename__ = "roads"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    road_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    longitude: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False)
    current_condition_index: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    traffic_volume: Mapped[int] = mapped_column(Integer, nullable=False)
    heavy_vehicle_percentage: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    rainfall: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    temperature: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    humidity: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    last_updated: Mapped[str] = mapped_column(String(10), nullable=False)

    predictions = relationship("PredictionModel", back_populates="road")
    digital_twins = relationship("DigitalTwinModel", back_populates="road", uselist=False)


class PredictionModel(Base):
    """Prediction model - matches Prediction from frontend types.ts."""

    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    road_segment_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("roads.id", ondelete="CASCADE"), nullable=False
    )
    predicted_condition_index: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    predicted_degradation: Mapped[float] = mapped_column(Numeric(8, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # Low, Medium, High
    prediction_date: Mapped[str] = mapped_column(String(10), nullable=False)
    month_offset: Mapped[int] = mapped_column(Integer, nullable=False)

    road = relationship("RoadModel", back_populates="predictions")


class DigitalTwinModel(Base):
    """Digital twin model - matches DigitalTwin from frontend types.ts."""

    __tablename__ = "digital_twins"

    id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    road_segment_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("roads.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    current_state: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    predicted_state: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    maintenance_recommendation: Mapped[str] = mapped_column(Text, nullable=False)

    road = relationship("RoadModel", back_populates="digital_twins")


def _decimal_to_float(val):
    """Convert Decimal to float for JSON serialization."""
    if val is None:
        return None
    if isinstance(val, Decimal):
        return float(val)
    return val
