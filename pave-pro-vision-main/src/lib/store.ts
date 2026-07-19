import type { RoadSegment, Prediction, DigitalTwin } from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

import { useState, useEffect } from 'react';
import type { RoadSegment, Prediction, DigitalTwin } from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

export async function addRoad(road: Omit<RoadSegment, 'id' | 'last_updated'>): Promise<RoadSegment> {
  const res = await fetch(`${API_BASE}/roads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(road),
  });
  if (!res.ok) throw new Error('Failed to add road');
  return res.json();
}

export function useData<T>(url: string, defaultValue: T) {
  const [data, setData] = useState<T>(defaultValue);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!url) return;
    let mounted = true;
    setLoading(true);
    fetch(`${API_BASE}${url}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed fetch');
        return res.json();
      })
      .then(json => {
        if (mounted) {
          setData(json);
          setLoading(false);
        }
      })
      .catch(() => {
        if (mounted) setLoading(false);
      });
    return () => { mounted = false; };
  }, [url]);

  return { data, loading };
}

export function useAllRoads() {
  return useData<RoadSegment[]>('/roads', []);
}

export function useDashboardStats() {
  return useData<{ total: number; high: number; medium: number; low: number; avgCondition: number }>(
    '/dashboard/stats',
    { total: 0, high: 0, medium: 0, low: 0, avgCondition: 0 }
  );
}

export function useRoad(id: string) {
  return useData<RoadSegment | undefined>(id ? `/roads/${id}` : '', undefined);
}

export function usePredictions(id: string) {
  const [data, setData] = useState<Prediction[]>([]);
  
  useEffect(() => {
    if (!id) return;
    let mounted = true;
    fetch(`${API_BASE}/predict/${id}`, { method: 'POST' })
      .then(r => r.json())
      .then(json => { if (mounted) setData([json]); })
      .catch(() => {});
    return () => { mounted = false; };
  }, [id]);

  return { data };
}

export function useDigitalTwin(id: string) {
  return useData<DigitalTwin | undefined>(id ? `/digital-twin/${id}` : '', undefined);
}

export function useAllDigitalTwins() {
  const { data: roads, loading } = useAllRoads();
  const [twins, setTwins] = useState<DigitalTwin[]>([]);

  useEffect(() => {
    if (loading || !roads.length) return;
    let mounted = true;
    Promise.all(
      roads.map(r => fetch(`${API_BASE}/digital-twin/${r.id}`).then(res => res.json()).catch(() => null))
    ).then(results => {
      if (mounted) {
        setTwins(results.filter(Boolean) as DigitalTwin[]);
      }
    });
    return () => { mounted = false; };
  }, [roads, loading]);

  return twins;
}
