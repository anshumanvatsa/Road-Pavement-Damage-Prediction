import type { RoadSegment, Prediction, DigitalTwin } from './types';

const API_BASE = 'http://127.0.0.1:8000';

/** Synchronous fetch - required to keep store API compatible with existing pages */
function syncFetch<T>(url: string, options?: { method?: string; body?: string }): T | undefined {
  try {
    const xhr = new XMLHttpRequest();
    xhr.open(options?.method || 'GET', url, false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(options?.body);
    if (xhr.status >= 200 && xhr.status < 300) {
      return (xhr.responseText ? JSON.parse(xhr.responseText) : null) as T;
    }
    if (xhr.status === 404) return undefined as T;
  } catch {
    // Backend unreachable - return undefined/empty
  }
  return undefined as T;
}

// --- API functions ---

export function fetchRoads(): RoadSegment[] {
  return syncFetch<RoadSegment[]>(`${API_BASE}/roads`) ?? [];
}

export function fetchRoadById(id: string): RoadSegment | undefined {
  return syncFetch<RoadSegment | undefined>(`${API_BASE}/roads/${id}`);
}

export function fetchPrediction(id: string): Prediction {
  const res = syncFetch<Prediction>(`${API_BASE}/predict/${id}`, {
    method: 'POST'
  });
  if (!res) throw new Error('Prediction failed');
  return res;
}


export function fetchDigitalTwin(id: string): DigitalTwin | undefined {
  return syncFetch<DigitalTwin | undefined>(`${API_BASE}/digital-twin/${id}`);
}

// --- Store exports (same names, backend-powered) ---

export function getAllRoads(): RoadSegment[] {
  return fetchRoads();
}

export function getRoad(id: string): RoadSegment | undefined {
  return fetchRoadById(id);
}

export function addRoad(road: Omit<RoadSegment, 'id' | 'last_updated'>): RoadSegment {
  const res = syncFetch<RoadSegment>(`${API_BASE}/roads`, {
    method: 'POST',
    body: JSON.stringify(road),
  });
  if (!res) throw new Error('Failed to add road');
  return res;
}

export function getPredictions(roadId: string): Prediction[] {
  const prediction = fetchPrediction(roadId);
  return prediction ? [prediction] : [];
}


export function getDigitalTwinForRoad(roadId: string): DigitalTwin | undefined {
  return fetchDigitalTwin(roadId);
}

export function getAllDigitalTwins(): DigitalTwin[] {
  const roads = fetchRoads();
  const twins: DigitalTwin[] = [];
  for (const road of roads) {
    const twin = fetchDigitalTwin(road.id);
    if (twin) twins.push(twin);
  }
  return twins;
}

export function getDashboardStats() {
  const res = syncFetch<{ total: number; high: number; medium: number; low: number; avgCondition: number }>(
    `${API_BASE}/dashboard/stats`
  );
  return res ?? { total: 0, high: 0, medium: 0, low: 0, avgCondition: 0 };
}
