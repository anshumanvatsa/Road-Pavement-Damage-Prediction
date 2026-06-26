import type { RiskLevel, RoadSegment, Prediction, DigitalTwin } from './types';

export function calculateDegradation(road: RoadSegment): number {
  const trafficFactor = (road.traffic_volume / 10000) * 2;
  const heavyVehicleFactor = (road.heavy_vehicle_percentage / 100) * 5;
  const rainfallFactor = (road.rainfall / 300) * 3;
  const tempFactor = Math.abs(road.temperature - 20) / 20 * 2;
  const humidityFactor = (road.humidity / 100) * 1.5;
  
  const baseDegradation = trafficFactor + heavyVehicleFactor + rainfallFactor + tempFactor + humidityFactor;
  const conditionMultiplier = 1 + (100 - road.current_condition_index) / 100;
  
  return Math.round(baseDegradation * conditionMultiplier * 100) / 100;
}

export function getRiskLevel(degradation: number): RiskLevel {
  if (degradation < 5) return 'Low';
  if (degradation <= 15) return 'Medium';
  return 'High';
}

export function getRecommendation(risk: RiskLevel): string {
  switch (risk) {
    case 'Low': return 'Monitor — routine inspection sufficient';
    case 'Medium': return 'Schedule preventive maintenance within 30 days';
    case 'High': return 'Immediate repair required — critical degradation detected';
  }
}

export function generatePredictions(road: RoadSegment): Prediction[] {
  const predictions: Prediction[] = [];
  let condition = road.current_condition_index;

  for (let month = 1; month <= 6; month++) {
    const seasonalFactor = 1 + 0.3 * Math.sin((month / 12) * Math.PI * 2);
    const degradation = calculateDegradation({ ...road, current_condition_index: condition }) * seasonalFactor * (month * 0.15);
    condition = Math.max(0, condition - degradation * 0.5);

    const date = new Date();
    date.setMonth(date.getMonth() + month);

    predictions.push({
      id: `pred-${road.id}-${month}`,
      road_segment_id: road.id,
      predicted_condition_index: Math.round(condition * 10) / 10,
      predicted_degradation: Math.round(degradation * 100) / 100,
      risk_level: getRiskLevel(degradation),
      prediction_date: date.toISOString().split('T')[0],
      month_offset: month,
    });
  }

  return predictions;
}

export function createDigitalTwin(road: RoadSegment): DigitalTwin {
  const predictions = generatePredictions(road);
  const worstPrediction = predictions.reduce((a, b) => 
    a.predicted_degradation > b.predicted_degradation ? a : b
  );
  const risk = worstPrediction.risk_level;

  return {
    id: `twin-${road.id}`,
    road_segment_id: road.id,
    current_state: road.current_condition_index,
    predicted_state: worstPrediction.predicted_condition_index,
    risk_level: risk,
    maintenance_recommendation: getRecommendation(risk),
  };
}
