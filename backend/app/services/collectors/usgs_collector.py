import aiohttp
import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
import json
from loguru import logger

class USGSEarthquakeCollector:
    """Collects real-time earthquake data from USGS API"""
    
    def __init__(self):
        self.base_url = "https://earthquake.usgs.gov/fdsnws/event/1/"
        self.source = "usgs"
        
    async def fetch_recent_earthquakes(self, minutes: int = 30, min_magnitude: float = 2.5) -> List[Dict[str, Any]]:
        """Fetch recent earthquakes from USGS"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=minutes)
        
        params = {
            'format': 'geojson',
            'starttime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'endtime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'minmagnitude': min_magnitude,
            'orderby': 'time'
        }
        
        url = f"{self.base_url}query"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"Fetched {len(data.get('features', []))} earthquakes from USGS")
                        return await self.process_earthquakes(data.get('features', []))
                    else:
                        logger.error(f"USGS API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching USGS data: {e}")
            return []
    
    async def process_earthquakes(self, features: List[Dict]) -> List[Dict]:
        """Process USGS earthquake data into our event format"""
        events = []
        
        for feature in features:
            try:
                props = feature['properties']
                geometry = feature['geometry']
                coords = geometry['coordinates']
                
                # Validate coordinates
                if len(coords) < 2:
                    logger.warning(f"Invalid coordinates for earthquake {feature['id']}")
                    continue
                    
                lon, lat = coords[0], coords[1]
                
                # Skip if coordinates are invalid
                if abs(lat) > 90 or abs(lon) > 180 or (lat == 0 and lon == 0):
                    logger.warning(f"Skipping earthquake with invalid coordinates: {lat}, {lon}")
                    continue
                
                # Calculate severity based on magnitude (scale 0-10)
                mag = props.get('mag', 0)
                if mag is None:
                    mag = 0
                severity = min(mag * 1.5, 10) if mag else 3
                
                # Determine threat level
                if mag >= 7.0:
                    threat = 'critical'
                elif mag >= 6.0:
                    threat = 'high'
                elif mag >= 5.0:
                    threat = 'medium'
                else:
                    threat = 'low'
                
                # Extract location name
                place = props.get('place', 'Unknown location')
                
                # Parse timestamp and make it timezone-aware
                timestamp = datetime.utcfromtimestamp(props['time'] / 1000).replace(tzinfo=timezone.utc)
                
                event = {
                    'id': feature['id'],
                    'type': 'earthquake',
                    'title': f"Magnitude {mag} earthquake - {place}",
                    'description': f"Earthquake detected. Depth: {coords[2] if len(coords) > 2 else 0} km. {place}",
                    'location': {
                        'type': 'Point',
                        'coordinates': [lon, lat]  # [lon, lat]
                    },
                    'location_name': place.split(',')[0].strip() if place else 'Unknown',
                    'country': self.extract_country(place),
                    'severity': round(severity, 1),
                    'threat_level': threat,
                    'occurred_at': timestamp.isoformat(),
                    'source': self.source,
                    'source_id': feature['id'],
                    'metadata': {
                        'magnitude': mag,
                        'depth': coords[2] if len(coords) > 2 else 0,
                        'felt': props.get('felt'),
                        'tsunami': props.get('tsunami'),
                        'alert': props.get('alert'),
                        'status': props.get('status')
                    }
                }
                events.append(event)
                
            except Exception as e:
                logger.error(f"Error processing earthquake: {e}")
                continue
                
        return events
    
    def extract_country(self, place: str) -> str:
        """Extract country from place string"""
        if not place:
            return 'Unknown'
        
        # Special case for Kermadec Islands
        if 'kermadec' in place.lower():
            return 'South Of Kermadec Islands'
        
        # Common patterns: "City, Country" or "Region, Country"
        parts = place.split(',')
        if len(parts) > 1:
            # Try to get the last part as country
            country = parts[-1].strip()
            # Clean up common issues
            country = country.replace('region', '').strip()
            return country if country else 'Unknown'
        return 'Unknown'