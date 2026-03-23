import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import re
from loguru import logger

class GDACSCollector:
    """Collects real-time natural disaster data from GDACS (Global Disaster Alert and Coordination System)"""
    
    def __init__(self):
        self.feed_url = "https://www.gdacs.org/xml/rss.xml"
        self.source = "gdacs"
        
    async def fetch_disasters(self) -> List[Dict[str, Any]]:
        """Fetch current natural disasters from GDACS RSS feed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.feed_url, timeout=10) as response:
                    if response.status == 200:
                        xml_data = await response.text()
                        events = await self.parse_rss(xml_data)
                        logger.info(f"Fetched {len(events)} disasters from GDACS")
                        return events
                    else:
                        logger.error(f"GDACS API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching GDACS data: {e}")
            return []
    
    async def parse_rss(self, xml_data: str) -> List[Dict]:
        """Parse GDACS RSS feed"""
        events = []
        
        try:
            root = ET.fromstring(xml_data)
            channel = root.find('channel')
            if channel is None:
                return events
                
            for item in channel.findall('item'):
                try:
                    event = await self.parse_rss_item(item)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.error(f"Error parsing RSS item: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing GDACS RSS: {e}")
            
        return events
    
    async def parse_rss_item(self, item) -> Optional[Dict]:
        """Parse individual RSS item with better coordinate extraction"""
        # Extract basic info
        title = item.find('title').text if item.find('title') is not None else ''
        description = item.find('description').text if item.find('description') is not None else ''
        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
        guid = item.find('guid').text if item.find('guid') is not None else ''
        
        # Try multiple ways to get coordinates
        lat = None
        lon = None
        
        # Method 1: Check for geo:lat and geo:long tags
        geo_lat = item.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}lat')
        geo_long = item.find('{http://www.w3.org/2003/01/geo/wgs84_pos#}long')
        
        if geo_lat is not None and geo_long is not None and geo_lat.text and geo_long.text:
            try:
                lat = float(geo_lat.text)
                lon = float(geo_long.text)
            except:
                pass
        
        # Method 2: Check for point coordinates
        if lat is None or lon is None:
            point = item.find('georss:point')
            if point is not None and point.text:
                try:
                    coords = point.text.strip().split()
                    if len(coords) >= 2:
                        lat = float(coords[0])
                        lon = float(coords[1])
                except:
                    pass
        
        # Method 3: Extract from description using regex
        if lat is None or lon is None:
            # Look for patterns like "Lat: -10.5, Lon: 165.5" or "latitude: -10.5, longitude: 165.5"
            lat_lon_patterns = [
                r'lat[^\d-]*([-+]?\d*\.?\d+)[^\d]*lon[^\d-]*([-+]?\d*\.?\d+)',
                r'latitude[^\d-]*([-+]?\d*\.?\d+)[^\d]*longitude[^\d-]*([-+]?\d*\.?\d+)',
                r'([-+]?\d+\.?\d*)[°\s]*[NS][,\s]*([-+]?\d+\.?\d*)[°\s]*[EW]',
            ]
            
            text = (title + ' ' + description).lower()
            for pattern in lat_lon_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        lat = float(match.group(1))
                        lon = float(match.group(2))
                        break
                    except:
                        pass
        
        # Method 4: Use country-based approximate coordinates if we have country info
        if (lat is None or lon is None) and (lat == 0 or lon == 0):
            country = self.extract_country(title, description)
            if country != 'Unknown':
                coords = self.get_country_coordinates(country)
                if coords:
                    lat, lon = coords
        
        # If still no coordinates, use a default but log a warning
        if lat is None or lon is None:
            logger.warning(f"Could not extract coordinates for event: {title[:50]}...")
            # Don't create event if we can't get coordinates
            return None
        
        # Validate coordinates
        if lat < -90 or lat > 90 or lon < -180 or lon > 180:
            logger.warning(f"Invalid coordinates for event {title[:50]}: {lat}, {lon}")
            return None
        
        # Determine disaster type from title
        event_type = self.determine_disaster_type(title)
        
        # Calculate severity and threat level
        severity, threat = self.calculate_severity(title, description)
        
        # Parse date
        try:
            # Remove timezone abbreviation for parsing
            date_str = pub_date.replace('GMT', '+0000')
            occurred_at = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
        except:
            occurred_at = datetime.now(timezone.utc)
        
        event = {
            'id': guid,
            'type': event_type,
            'title': title[:200],
            'description': description[:500],
            'location': {
                'type': 'Point',
                'coordinates': [lon, lat]  # GeoJSON uses [lon, lat] order
            },
            'location_name': self.extract_location_name(title, description),
            'country': self.extract_country(title, description),
            'severity': severity,
            'threat_level': threat,
            'occurred_at': occurred_at.isoformat(),
            'source': self.source,
            'source_id': guid,
            'metadata': {
                'raw_title': title,
                'raw_description': description,
                'pub_date': pub_date
            }
        }
        
        return event
    
    def get_country_coordinates(self, country: str) -> Optional[List[float]]:
        """Get approximate coordinates for a country"""
        coordinates = {
            'South Of Kermadec Islands': [-178.0, -30.0],
            'Kermadec Islands': [-178.0, -29.0],
            'New Zealand': [174.0, -41.0],
            'Australia': [133.0, -27.0],
            'USA': [-98.0, 39.0],
            'United States': [-98.0, 39.0],
            'Japan': [138.0, 36.0],
            'Russia': [105.0, 61.0],
            'China': [104.0, 35.0],
            'India': [78.0, 20.0],
            'Indonesia': [118.0, -2.0],
            'Philippines': [122.0, 12.0],
            'Italy': [12.0, 42.0],
            'Greece': [22.0, 39.0],
            'Turkey': [35.0, 39.0],
            'Iran': [53.0, 32.0],
            'Pakistan': [69.0, 30.0],
            'Afghanistan': [66.0, 33.0],
            'Mexico': [-102.0, 23.0],
            'Canada': [-106.0, 56.0],
            'Brazil': [-51.0, -14.0],
            'Argentina': [-63.0, -38.0],
            'Chile': [-71.0, -35.0],
            'Peru': [-75.0, -9.0],
            'Colombia': [-74.0, 4.0],
            'Venezuela': [-66.0, 7.0],
            'South Africa': [24.0, -29.0],
            'Nigeria': [8.0, 9.0],
            'Egypt': [29.0, 26.0],
            'Kenya': [37.0, 1.0],
            'Ethiopia': [39.0, 8.0],
            'Sudan': [30.0, 15.0],
            'DRC': [23.0, -2.0],
            'Congo': [23.0, -2.0],
            'Myanmar': [96.0, 21.0],
            'Thailand': [101.0, 15.0],
            'Vietnam': [108.0, 14.0],
            'France': [2.0, 46.0],
            'Germany': [10.0, 51.0],
            'UK': [-3.0, 55.0],
            'United Kingdom': [-3.0, 55.0],
        }
        
        # Try exact match
        if country in coordinates:
            return coordinates[country]
        
        # Try partial match
        for key, coords in coordinates.items():
            if key.lower() in country.lower() or country.lower() in key.lower():
                return coords
        
        # Default to Null Island if no match (but we'll skip instead)
        return None
    
    def determine_disaster_type(self, title: str) -> str:
        """Determine disaster type from title"""
        title_lower = title.lower()
        
        if 'earthquake' in title_lower:
            return 'earthquake'
        elif 'cyclone' in title_lower or 'hurricane' in title_lower or 'typhoon' in title_lower:
            return 'storm'
        elif 'flood' in title_lower:
            return 'flood'
        elif 'tsunami' in title_lower:
            return 'tsunami'
        elif 'volcano' in title_lower or 'eruption' in title_lower:
            return 'volcano'
        elif 'wildfire' in title_lower or 'fire' in title_lower:
            return 'wildfire'
        elif 'drought' in title_lower:
            return 'drought'
        else:
            return 'natural_disaster'
    
    def calculate_severity(self, title: str, description: str) -> tuple:
        """Calculate severity and threat level"""
        text = (title + ' ' + description).lower()
        
        # Look for magnitude indicators
        mag_match = re.search(r'magnitude (?:M )?(\d+\.?\d*)', text, re.IGNORECASE)
        if mag_match:
            mag = float(mag_match.group(1))
            severity = min(mag * 1.5, 10)
        else:
            # Check for severity keywords
            if 'catastrophic' in text or 'devastating' in text or 'massive' in text:
                severity = 9.0
            elif 'severe' in text or 'major' in text or 'powerful' in text:
                severity = 7.0
            elif 'moderate' in text or 'strong' in text:
                severity = 5.0
            else:
                severity = 4.0
        
        # Determine threat level
        if severity >= 8.0:
            threat = 'critical'
        elif severity >= 6.0:
            threat = 'high'
        elif severity >= 4.0:
            threat = 'medium'
        else:
            threat = 'low'
            
        return round(severity, 1), threat
    
    def extract_location_name(self, title: str, description: str) -> str:
        """Extract location name from title/description"""
        text = title + ' ' + description
        
        # Try to find location in format "in LOCATION" or "at LOCATION"
        location_match = re.search(r'(?:in|at|near) ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
        if location_match:
            return location_match.group(1)
        
        return 'Unknown'
    
    def extract_country(self, title: str, description: str) -> str:
        """Extract country from title/description"""
        text = title + ' ' + description
        
        # Special case for Kermadec Islands
        if 'kermadec' in text.lower():
            return 'South Of Kermadec Islands'
        
        # List of countries to check
        countries = [
            'USA', 'United States', 'America', 'Canada', 'Mexico', 'Brazil', 'Argentina',
            'UK', 'United Kingdom', 'France', 'Germany', 'Italy', 'Spain', 'Portugal',
            'Russia', 'China', 'Japan', 'India', 'Australia', 'New Zealand',
            'Indonesia', 'Philippines', 'Vietnam', 'Thailand', 'Malaysia',
            'South Africa', 'Egypt', 'Nigeria', 'Kenya', 'Morocco',
            'Greece', 'Turkey', 'Iran', 'Pakistan', 'Afghanistan',
            'Chile', 'Peru', 'Colombia', 'Venezuela',
            'Sudan', 'Ethiopia', 'DRC', 'Congo', 'Myanmar'
        ]
        
        for country in countries:
            if country.lower() in text.lower():
                return country
        
        return 'Unknown'