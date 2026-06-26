import type { RoadSegment } from './types';

const roadNames = [
  'Main Street', 'Highway 101', 'Oak Avenue', 'Industrial Blvd', 'River Road',
  'Cedar Lane', 'Park Drive', 'Market Street', 'Bridge Road', 'Elm Street',
  'Sunset Boulevard', 'Canyon Road', 'Harbor Drive', 'Mountain Pass', 'Valley Way',
  'Airport Road', 'University Ave', 'Central Expressway', 'Bay Street', 'Lake Drive',
  'Commerce Way', 'Factory Road', 'Orchard Lane', 'Coastal Highway', 'Metro Boulevard',
  'Rail Corridor', 'Tech Park Drive', 'Heritage Road', 'Forest Avenue', 'Marsh Creek Rd',
  'Summit Drive', 'Pier Street', 'Arena Boulevard', 'Campus Drive', 'Quarry Road',
  'Vineyard Lane', 'Mill Street', 'Dock Road', 'Basin Avenue', 'Ridge Way',
  'Lagoon Drive', 'Prairie Road', 'Bluff Street', 'Creek Crossing', 'Hillcrest Ave',
  'Meadow Lane', 'Terrace Drive', 'Canal Street', 'Spring Road', 'Crest Avenue',
];

const locations = [
  'Downtown Core', 'North District', 'South Industrial Zone', 'East Waterfront', 'West Suburbs',
  'Central Business', 'Port Area', 'University Quarter', 'Tech Hub', 'Residential North',
  'Old Town', 'New Development', 'Airport Zone', 'Commercial Strip', 'River District',
  'Hillside', 'Coastal Zone', 'Transit Corridor', 'Heritage District', 'Innovation Park',
];

function seededRandom(seed: number): () => number {
  let s = seed;
  return () => {
    s = (s * 16807 + 0) % 2147483647;
    return s / 2147483647;
  };
}

export function generateSampleRoads(count = 50): RoadSegment[] {
  const rand = seededRandom(42);
  const roads: RoadSegment[] = [];

  for (let i = 0; i < count; i++) {
    const daysAgo = Math.floor(rand() * 90);
    const date = new Date();
    date.setDate(date.getDate() - daysAgo);

    roads.push({
      id: `road-${String(i + 1).padStart(3, '0')}`,
      road_name: roadNames[i % roadNames.length],
      location: locations[Math.floor(rand() * locations.length)],
      latitude: 37.3 + rand() * 0.5,
      longitude: -122.0 - rand() * 0.5,
      current_condition_index: Math.round((30 + rand() * 70) * 10) / 10,
      traffic_volume: Math.round(1000 + rand() * 19000),
      heavy_vehicle_percentage: Math.round(rand() * 40 * 10) / 10,
      rainfall: Math.round(rand() * 300 * 10) / 10,
      temperature: Math.round((5 + rand() * 40) * 10) / 10,
      humidity: Math.round((20 + rand() * 70) * 10) / 10,
      last_updated: date.toISOString().split('T')[0],
    });
  }

  return roads;
}
