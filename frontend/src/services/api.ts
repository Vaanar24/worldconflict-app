import axios from 'axios';
import { MapBounds, Filters } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

console.log('🚀 API Base URL:', API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// ============ Event Endpoints ============

export const fetchEvents = async (bounds: MapBounds, filters?: Filters) => {
  try {
    const bbox = `${bounds.minLon},${bounds.minLat},${bounds.maxLon},${bounds.maxLat}`;
    const params: any = {
      bbox,
      hours: filters?.timeRange || 24,
      limit: 1000
    };

    if (filters?.eventType) params.event_type = filters.eventType;
    if (filters?.threatLevel) params.threat_level = filters.threatLevel;

    const response = await api.get('/events', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching events:', error);
    return { type: 'FeatureCollection', features: [] };
  }
};

export const fetchEventStats = async (hours: number = 24) => {
  try {
    const response = await api.get('/events/stats', { params: { hours } });
    return response.data;
  } catch (error) {
    console.error('Error fetching stats:', error);
    return {
      total_events: 0,
      total_casualties: 0,
      active_conflicts: 0,
      by_type: {},
      by_threat_level: {},
      hotspots: []
    };
  }
};

// ============ Historical Data Endpoints ============

export interface ConflictTrendData {
  timestamp: string;
  event_count: number;
  severity_avg: number;
  active_conflicts: number;
}

export const fetchConflictTrends = async (days: number = 90, granularity: string = 'day') => {
  try {
    const response = await api.get('/historical/conflict-trends', {
      params: { days, granularity }
    });
    console.log('📊 Conflict trends response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching conflict trends:', error);
    // Return mock data for development/fallback
    return {
      data: generateMockConflictTrends(days, granularity)
    };
  }
};

export interface CasualtyTrendData {
  timestamp: string;
  military_casualties: number;
  civilian_casualties: number;
  total_casualties: number;
  source: string;
}

export const fetchCasualtyTrends = async (days: number = 90) => {
  try {
    const response = await api.get('/historical/casualty-trends', {
      params: { days }
    });
    console.log('📊 Casualty trends response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching casualty trends:', error);
    // Return mock data for development/fallback
    return {
      data: generateMockCasualtyTrends(days)
    };
  }
};

export interface TerritorialChange {
  id: string;
  location_name: string;
  country: string;
  from_control: string;
  to_control: string;
  changed_at: string;
  coordinates: [number, number];
  significance: string;
  source: string;
}

export const fetchTerritorialChanges = async () => {
  try {
    const response = await api.get('/historical/territorial-changes');
    console.log('📍 Territorial changes response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching territorial changes:', error);
    // Return mock data for development
    return {
      changes: generateMockTerritorialChanges()
    };
  }
};

export interface HeatmapPoint {
  coordinates: [number, number];
  intensity: number;
  radius: number;
  timestamp: string;
  event_type: string;
}

export const fetchHeatmapData = async (bounds: MapBounds) => {
  try {
    const bbox = `${bounds.minLon},${bounds.minLat},${bounds.maxLon},${bounds.maxLat}`;
    const response = await api.get('/historical/heatmap', { params: { bbox } });
    return response.data.data || [];
  } catch (error) {
    console.error('Error fetching heatmap data:', error);
    return generateMockHeatmapData(bounds);
  }
};

export interface HistoricalStatistics {
  period_days: number;
  summary: {
    total_events: number;
    avg_daily_events: number;
    total_casualties: number;
    peak_event_day: string;
    peak_event_count: number;
  };
}

export const fetchHistoricalStatistics = async (days: number = 90) => {
  try {
    const response = await api.get('/historical/statistics', {
      params: { days }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching historical statistics:', error);
    return {
      period_days: days,
      summary: {
        total_events: 0,
        avg_daily_events: 0,
        total_casualties: 0,
        peak_event_day: '',
        peak_event_count: 0
      }
    };
  }
};

// ============ Camera Endpoints ============

export interface CameraFeed {
  id: string;
  title: string;
  description: string;
  url: string;
  thumbnail: string;
  location_name: string;
  country: string;
  feed_type: string;
  status: string;
}

export const fetchCameraFeeds = async (location?: string, feedType?: string) => {
  try {
    const params: any = {};
    if (location) params.location = location;
    if (feedType) params.feed_type = feedType;
    
    const response = await api.get('/cameras', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching camera feeds:', error);
    return { feeds: [] };
  }
};

export const fetchNearbyCameras = async (lat: number, lng: number, radiusKm: number = 100) => {
  try {
    const response = await api.get('/cameras/nearby', {
      params: { lat, lng, radius_km: radiusKm }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching nearby cameras:', error);
    return { cameras: [] };
  }
};

// ============ Debug Endpoints ============

export const fetchDebugEvents = async () => {
  try {
    const response = await api.get('/events/debug/all');
    return response.data;
  } catch (error) {
    console.error('Error fetching debug events:', error);
    return null;
  }
};

// ============ Mock Data Generators (Fallback) ============

const generateMockConflictTrends = (days: number, granularity: string) => {
  const data = [];
  const now = new Date();
  const step = granularity === 'day' ? 1 : granularity === 'week' ? 7 : 30;
  
  for (let i = days; i >= 0; i -= step) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    // Generate realistic-looking trend data
    const baseValue = 30 + Math.sin(i / 30) * 15;
    const spike = i === 45 ? 50 : i === 90 ? 80 : 0;
    
    data.push({
      timestamp: date.toISOString(),
      event_count: Math.floor(baseValue + spike + Math.random() * 10),
      severity_avg: Number((5 + Math.sin(i / 45) * 2 + Math.random()).toFixed(1)),
      active_conflicts: Math.floor(10 + Math.sin(i / 60) * 5 + spike / 10)
    });
  }
  
  return data;
};

const generateMockCasualtyTrends = (days: number) => {
  const data = [];
  const now = new Date();
  
  for (let i = days; i >= 0; i -= 1) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);
    
    const baseMilitary = 200 + Math.sin(i / 30) * 100;
    const baseCivilian = 150 + Math.cos(i / 45) * 80;
    const spike = i === 45 ? 300 : i === 90 ? 500 : 0;
    
    data.push({
      timestamp: date.toISOString(),
      military_casualties: Math.floor(baseMilitary + spike / 2 + Math.random() * 50),
      civilian_casualties: Math.floor(baseCivilian + spike / 3 + Math.random() * 40),
      total_casualties: Math.floor(baseMilitary + baseCivilian + spike + Math.random() * 80),
      source: "estimated"
    });
  }
  
  return data;
};

const generateMockTerritorialChanges = (): TerritorialChange[] => {
  const now = new Date();
  return [
    {
      id: "mock_1",
      location_name: "Kharkiv Region",
      country: "Ukraine",
      from_control: "Ukraine",
      to_control: "Russia",
      changed_at: new Date(now.getTime() - 45 * 24 * 60 * 60 * 1000).toISOString(),
      coordinates: [36.25, 49.98],
      significance: "strategic",
      source: "Mock Data"
    },
    {
      id: "mock_2",
      location_name: "Bakhmut",
      country: "Ukraine",
      from_control: "Ukraine",
      to_control: "Russia",
      changed_at: new Date(now.getTime() - 120 * 24 * 60 * 60 * 1000).toISOString(),
      coordinates: [38.0, 48.6],
      significance: "strategic",
      source: "Mock Data"
    },
    {
      id: "mock_3",
      location_name: "Northern Gaza",
      country: "Palestine",
      from_control: "Hamas",
      to_control: "IDF",
      changed_at: new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      coordinates: [34.5, 31.55],
      significance: "tactical",
      source: "Mock Data"
    },
    {
      id: "mock_4",
      location_name: "Khartoum",
      country: "Sudan",
      from_control: "RSF",
      to_control: "SAF",
      changed_at: new Date(now.getTime() - 15 * 24 * 60 * 60 * 1000).toISOString(),
      coordinates: [32.55, 15.5],
      significance: "strategic",
      source: "Mock Data"
    }
  ];
};

const generateMockHeatmapData = (bounds: MapBounds): HeatmapPoint[] => {
  const points: HeatmapPoint[] = [];
  
  // Major conflict zones
  const zones = [
    { coords: [30.5, 50.5] as [number, number], intensity: 95, radius: 150 },  // Ukraine
    { coords: [34.5, 31.5] as [number, number], intensity: 90, radius: 80 },   // Gaza
    { coords: [32.5, 15.5] as [number, number], intensity: 85, radius: 200 },   // Sudan
    { coords: [96.5, 22.0] as [number, number], intensity: 80, radius: 180 },   // Myanmar
    { coords: [29.0, -1.5] as [number, number], intensity: 75, radius: 250 },   // DR Congo
    { coords: [39.5, 13.5] as [number, number], intensity: 70, radius: 150 },   // Ethiopia
    { coords: [-72.5, 18.5] as [number, number], intensity: 65, radius: 80 },   // Haiti
    { coords: [44.5, 12.5] as [number, number], intensity: 60, radius: 100 },   // Yemen
  ];
  
  for (const zone of zones) {
    const [lon, lat] = zone.coords;
    // Check if the zone is within the bounds
    if (lon >= bounds.minLon && lon <= bounds.maxLon && 
        lat >= bounds.minLat && lat <= bounds.maxLat) {
      points.push({
        coordinates: zone.coords,
        intensity: zone.intensity,
        radius: zone.radius,
        timestamp: new Date().toISOString(),
        event_type: "conflict"
      });
    }
  }
  
  return points;
};

export default api;