import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import { Event, Filters } from '../types';
import { fetchEvents, fetchEventStats } from '../services/api';

interface EventContextType {
  events: Event[];
  filters: Filters;
  setFilters: (filters: Filters) => void;
  selectedEvent: Event | null;
  setSelectedEvent: (event: Event | null) => void;
  loading: boolean;
  stats: any;
  loadEventsForBounds: (bounds: any) => Promise<void>;
}

const EventContext = createContext<EventContextType | undefined>(undefined);

export const useEventContext = () => {
  const context = useContext(EventContext);
  if (!context) throw new Error('useEventContext must be used within EventProvider');
  return context;
};

export const EventProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [filters, setFilters] = useState<Filters>({ timeRange: 24 });
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchEventStats(filters.timeRange).then(setStats);
  }, [filters.timeRange]);

  const loadEventsForBounds = useCallback(async (bounds: any) => {
    setLoading(true);
    try {
      const data = await fetchEvents(bounds, filters);
      setEvents(data.features?.map((f: any) => f.properties) || []);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadEventsForBounds({ minLon: -180, minLat: -90, maxLon: 180, maxLat: 90 });
  }, [loadEventsForBounds, filters.eventType, filters.threatLevel, filters.timeRange]);

  return (
    <EventContext.Provider value={{
      events, filters, setFilters, selectedEvent, setSelectedEvent, loading, stats, loadEventsForBounds
    }}>
      {children}
    </EventContext.Provider>
  );
};