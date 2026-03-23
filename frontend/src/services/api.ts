import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export interface MapBounds {
  minLon: number;
  minLat: number;
  maxLon: number;
  maxLat: number;
}

export interface Filters {
  eventType?: string;
  threatLevel?: string;
  timeRange: number;
}

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