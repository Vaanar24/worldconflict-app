export interface ConflictTrend {
  timestamp: string;
  event_count: number;
  severity_avg: number;
  active_conflicts: number;
}

export interface CasualtyTrend {
  timestamp: string;
  military_casualties: number;
  civilian_casualties: number;
  total_casualties: number;
  source: string;
}

export interface TerritorialChange {
  id: string;
  location_name: string;
  country: string;
  from_control: string;
  to_control: string;
  changed_at: string;
  coordinates: [number, number];
  significance: 'strategic' | 'symbolic' | 'tactical';
  source: string;
}

export interface HeatmapPoint {
  coordinates: [number, number];
  intensity: number;
  radius: number;
  timestamp: string;
  event_type: string;
}

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