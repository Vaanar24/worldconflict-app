import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useEventContext } from '../context/EventContext';

// Fix for default markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const getEventIcon = (type: string, threatLevel: string) => {
  const colors: Record<string, string> = {
    critical: '#ff0000',
    high: '#ff4500',
    medium: '#ff8c00',
    low: '#ffd700',
  };

  const color = colors[threatLevel] || '#ff8c00';
  const size = threatLevel === 'critical' ? 28 : 24;
  
  return L.divIcon({
    html: `<div style="
      background-color: ${color};
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 0 20px ${color};
      animation: ${threatLevel === 'critical' ? 'pulse 1.5s infinite' : 'none'};
      cursor: pointer;
    "></div>
    <style>
      @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.3); opacity: 0.9; }
        100% { transform: scale(1); opacity: 1; }
      }
    </style>`,
    className: 'custom-marker',
    iconSize: [size, size],
    iconAnchor: [size/2, size/2],
  });
};

function MapBoundsHandler() {
  const map = useMap();
  const { loadEventsForBounds } = useEventContext();
  
  useEffect(() => {
    const handleMoveEnd = () => {
      const bounds = map.getBounds();
      loadEventsForBounds({
        minLon: bounds.getWest(),
        minLat: bounds.getSouth(),
        maxLon: bounds.getEast(),
        maxLat: bounds.getNorth()
      });
    };
    
    map.on('moveend', handleMoveEnd);
    handleMoveEnd();
    
    return () => { map.off('moveend', handleMoveEnd); };
  }, [map, loadEventsForBounds]);
  
  return null;
}

function MapCenterer() {
  const map = useMap();
  const { selectedEvent } = useEventContext();
  
  useEffect(() => {
    if (selectedEvent?.location?.coordinates) {
      const [lon, lat] = selectedEvent.location.coordinates;
      map.setView([lat, lon], 6, { animate: true });
    }
  }, [selectedEvent, map]);
  
  return null;
}

const WorldMap: React.FC = () => {
  const { events } = useEventContext();
  
  const validEvents = events.filter(e => 
    e?.location?.coordinates && 
    e.location.coordinates.length >= 2
  );

  return (
    <MapContainer
      center={[30, 0]}
      zoom={2}
      style={{ height: '100%', width: '100%' }}
      minZoom={2}
      maxBounds={[[-90, -180], [90, 180]]}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
      />
      
      <MapBoundsHandler />
      <MapCenterer />
      
      {validEvents.map((event) => {
        const [lon, lat] = event.location.coordinates;
        return (
          <Marker
            key={event.id}
            position={[lat, lon]}
            icon={getEventIcon(event.type, event.threat_level)}
          >
            <Popup>
              <div style={{ minWidth: '200px' }}>
                <h3 style={{ margin: '0 0 8px 0' }}>{event.title}</h3>
                <p><strong>Type:</strong> {event.type.replace('_', ' ')}</p>
                <p><strong>Location:</strong> {event.location_name}, {event.country}</p>
                <p><strong>Threat:</strong> {event.threat_level}</p>
                {event.casualties?.total && (
                  <p><strong>Casualties:</strong> {event.casualties.total.toLocaleString()}+</p>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
      
      <div style={{
        position: 'absolute',
        top: '10px',
        right: '10px',
        background: 'rgba(0,0,0,0.8)',
        color: 'white',
        padding: '8px 16px',
        borderRadius: '20px',
        zIndex: 1000,
        fontSize: '14px',
        fontWeight: 'bold'
      }}>
        {validEvents.length} events
      </div>
    </MapContainer>
  );
};

export default WorldMap;