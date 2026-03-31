import React, { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';
import { Button, IconButton, Tooltip } from '@mui/material';
import VideocamIcon from '@mui/icons-material/Videocam';
import HeatmapIcon from '@mui/icons-material/Map';
import { useEventContext } from '../context/EventContext';
import { fetchHeatmapData } from '../services/api';
import HeatmapLayer from './HeatmapLayer';

// Fix for default markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const getEventIcon = (type: string, threatLevel: string, verified: boolean) => {
  const colors: Record<string, string> = {
    critical: '#ff0000',
    high: '#ff4500',
    medium: '#ff8c00',
    low: '#ffd700',
    ceasefire: '#4169e1',
  };

  const color = colors[threatLevel] || '#ff8c00';
  const size = threatLevel === 'critical' ? 28 : threatLevel === 'high' ? 24 : 20;
  const borderColor = verified ? 'white' : '#aaa';
  const pulsing = threatLevel === 'critical' ? 'pulse 1.5s infinite' : 'none';
  
  return L.divIcon({
    html: `<div style="
      background-color: ${color};
      width: ${size}px;
      height: ${size}px;
      border-radius: 50%;
      border: 3px solid ${borderColor};
      box-shadow: 0 0 20px ${color};
      animation: ${pulsing};
      cursor: pointer;
      transition: transform 0.2s;
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
  const [heatmapVisible, setHeatmapVisible] = useState(false);
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [currentBounds, setCurrentBounds] = useState<any>(null);
  const [showLegend, setShowLegend] = useState(true);

  const validEvents = events.filter(e => 
    e?.location?.coordinates && 
    e.location.coordinates.length >= 2 &&
    !(e.location.coordinates[0] === 0 && e.location.coordinates[1] === 0)
  );

  const handleShowCamera = (location: string, country: string) => {
    window.dispatchEvent(new CustomEvent('showCamera', { 
      detail: { location, country }
    }));
  };

  const loadHeatmapData = useCallback(async (bounds: any) => {
    if (heatmapVisible && bounds) {
      try {
        const data = await fetchHeatmapData(bounds);
        setHeatmapData(data);
      } catch (error) {
        console.error('Error loading heatmap data:', error);
      }
    }
  }, [heatmapVisible]);

  const onBoundsChange = useCallback((bounds: any) => {
    setCurrentBounds(bounds);
    loadHeatmapData(bounds);
  }, [loadHeatmapData]);

  useEffect(() => {
    if (heatmapVisible && currentBounds) {
      loadHeatmapData(currentBounds);
    }
  }, [heatmapVisible, currentBounds, loadHeatmapData]);

  return (
    <>
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
        
        {/* Heatmap Layer */}
        {heatmapVisible && heatmapData.length > 0 && (
          <HeatmapLayer data={heatmapData} visible={heatmapVisible} />
        )}
        
        {/* Event Markers */}
        {validEvents.map((event) => {
          const [lon, lat] = event.location.coordinates;
          return (
            <Marker
              key={event.id}
              position={[lat, lon]}
              icon={getEventIcon(event.type, event.threat_level, event.verified)}
            >
              <Popup>
                <div style={{ minWidth: '250px', maxWidth: '300px' }}>
                  <h3 style={{ margin: '0 0 8px 0', color: '#333' }}>
                    {event.title}
                    {event.verified && ' ✓'}
                  </h3>
                  <p style={{ margin: '4px 0' }}>
                    <strong>Type:</strong> {event.type.replace('_', ' ')}
                  </p>
                  <p style={{ margin: '4px 0' }}>
                    <strong>Location:</strong> {event.location_name}, {event.country}
                  </p>
                  <p style={{ margin: '4px 0' }}>
                    <strong>Threat:</strong>{' '}
                    <span style={{ 
                      color: event.threat_level === 'critical' ? 'red' : 
                             event.threat_level === 'high' ? 'orange' : 
                             event.threat_level === 'medium' ? 'blue' : 'green',
                      fontWeight: 'bold',
                      textTransform: 'uppercase'
                    }}>
                      {event.threat_level}
                    </span>
                  </p>
                  {event.casualties?.total && (
                    <p style={{ margin: '4px 0', color: '#d32f2f' }}>
                      <strong>Casualties:</strong> {event.casualties.total.toLocaleString()}+
                    </p>
                  )}
                  
                  {/* Camera Button */}
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<VideocamIcon />}
                    onClick={() => handleShowCamera(event.location_name, event.country)}
                    sx={{ mt: 1, textTransform: 'none' }}
                  >
                    View Live Camera
                  </Button>
                </div>
              </Popup>
            </Marker>
          );
        })}
        
        {/* Map Controls Overlay */}
        <div style={{
          position: 'absolute',
          bottom: '20px',
          right: '10px',
          zIndex: 1000,
          background: 'rgba(0,0,0,0.8)',
          borderRadius: '8px',
          padding: '8px',
          backdropFilter: 'blur(5px)',
        }}>
          <Tooltip title="Heatmap Layer" placement="left">
            <IconButton 
              size="small" 
              onClick={() => setHeatmapVisible(!heatmapVisible)}
              sx={{ 
                color: heatmapVisible ? '#ff6b6b' : 'white',
                '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' }
              }}
            >
              <HeatmapIcon />
            </IconButton>
          </Tooltip>
        </div>
        
        {/* Legend */}
        {showLegend && (
          <div style={{
            position: 'absolute',
            bottom: '20px',
            left: '10px',
            zIndex: 1000,
            background: 'rgba(0,0,0,0.8)',
            borderRadius: '8px',
            padding: '8px 12px',
            backdropFilter: 'blur(5px)',
            fontSize: '12px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span>Legend</span>
              <IconButton 
                size="small" 
                onClick={() => setShowLegend(false)} 
                sx={{ color: 'white', p: 0, '&:hover': { backgroundColor: 'transparent' } }}
              >
                ×
              </IconButton>
            </div>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <div><span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#ff0000', marginRight: '4px' }}></span> Critical</div>
              <div><span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#ff4500', marginRight: '4px' }}></span> High</div>
              <div><span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#ff8c00', marginRight: '4px' }}></span> Medium</div>
              <div><span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#ffd700', marginRight: '4px' }}></span> Low</div>
              <div><span style={{ display: 'inline-block', width: '12px', height: '12px', borderRadius: '50%', background: '#4169e1', marginRight: '4px' }}></span> Ceasefire</div>
            </div>
          </div>
        )}
        
        {/* Event Counter */}
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
          fontWeight: 'bold',
          backdropFilter: 'blur(5px)'
        }}>
          {validEvents.length} active events
        </div>
      </MapContainer>
    </>
  );
};

export default WorldMap;