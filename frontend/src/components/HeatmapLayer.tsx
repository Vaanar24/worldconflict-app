import React, { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

interface HeatmapPoint {
  coordinates: [number, number];
  intensity: number;
  radius: number;
}

interface HeatmapLayerProps {
  data: HeatmapPoint[];
  visible: boolean;
}

const HeatmapLayer: React.FC<HeatmapLayerProps> = ({ data, visible }) => {
  const map = useMap();
  const heatmapRef = useRef<any>(null);

  useEffect(() => {
    if (!visible || !data.length) {
      if (heatmapRef.current) {
        map.removeLayer(heatmapRef.current);
        heatmapRef.current = null;
      }
      return;
    }

    const heatData = data.map(point => [
      point.coordinates[1],
      point.coordinates[0],
      point.intensity / 100
    ]);

    if (heatmapRef.current) {
      map.removeLayer(heatmapRef.current);
    }

    // @ts-ignore - leaflet.heat is imported
    heatmapRef.current = L.heatLayer(heatData, {
      radius: 25,
      blur: 15,
      maxZoom: 10,
      minOpacity: 0.3,
      gradient: {
        0.2: '#00ff00',
        0.4: '#ffff00',
        0.6: '#ff8800',
        0.8: '#ff4400',
        1.0: '#ff0000'
      }
    }).addTo(map);

    return () => {
      if (heatmapRef.current) {
        map.removeLayer(heatmapRef.current);
        heatmapRef.current = null;
      }
    };
  }, [data, map, visible]);

  return null;
};

export default HeatmapLayer;