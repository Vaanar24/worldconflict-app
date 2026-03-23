export interface Casualties {
  military?: number;
  civilian?: number;
  total?: number;
  source?: string;
}

export interface ConflictDetails {
  parties_involved: string[];
  front_line?: string;
  strategic_importance?: string;
  civilian_impact?: string;
  infrastructure_damage?: string;
}

export interface Event {
  id: string;
  type: 'conflict' | 'battle' | 'air_strike' | 'artillery' | 'ground_assault' | 
        'ceasefire' | 'peace_talks' | 'troop_movement' | 'civilian_casualty' | 
        'military_casualty' | 'territory_change' | 'sanctions' | 'diplomatic' |
        'earthquake' | 'storm' | 'flood';
  title: string;
  description: string;
  location: {
    type: 'Point';
    coordinates: [number, number];
  };
  location_name: string;
  country: string;
  region: string;
  severity: number;
  threat_level: 'critical' | 'high' | 'medium' | 'low' | 'ceasefire';
  casualties?: Casualties;
  conflict_details?: ConflictDetails;
  occurred_at: string;
  source: string;
  source_id: string;
  verified: boolean;
  metadata?: Record<string, any>;
}

export interface EventFeature {
  type: 'Feature';
  geometry: {
    type: 'Point';
    coordinates: [number, number];
  };
  properties: Event;
}

export interface EventCollection {
  type: 'FeatureCollection';
  features: EventFeature[];
}

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
  showCasualties?: boolean;
  showVerifiedOnly?: boolean;
}