export type RiskLevel = 'Low' | 'Medium' | 'High';

export interface RoadSegment {
  id: string;
  road_name: string;
  location: string;
  latitude: number;
  longitude: number;
  current_condition_index: number;
  traffic_volume: number;
  heavy_vehicle_percentage: number;
  rainfall: number;
  temperature: number;
  humidity: number;
  last_updated: string;
}

export interface Prediction {
  id: string;
  road_segment_id: string;
  predicted_condition_index: number;
  predicted_degradation: number;
  risk_level: RiskLevel;
  prediction_date: string;
  month_offset: number;
}

export interface DigitalTwin {
  id: string;
  road_segment_id: string;
  current_state: number;
  predicted_state: number;
  risk_level: RiskLevel;
  maintenance_recommendation: string;
}
