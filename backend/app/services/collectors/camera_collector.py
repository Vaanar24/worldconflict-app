import aiohttp
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any
import re
from loguru import logger

class LiveCameraCollector:
    """Collects live camera feeds from various sources"""
    
    def __init__(self):
        self.sources = {
            "youtube": {
                "ukraine_live": "UCX6OQ3DkcsbYNE6H8uQQuVA",  # Ukraine live cams
                "gaza_live": "UCPIhBH0e_7HCL-S8o6yoT6Q",      # Gaza live feeds
                "earthquake_cams": "UC6zHYEnBuTGMi0FBg-CF0Zg", # Earthquake monitoring
                "world_cams": "UC3nA5cRjQaVZvXpZqZxZpZQ"       # Global live cams
            },
            "earthcam": {
                "api_key": None  # Free API available
            },
            "weather_cams": {
                "base_url": "https://api.weather.gov/cameras"
            }
        }
    
    async def fetch_youtube_streams(self) -> List[Dict[str, Any]]:
        """Fetch live YouTube streams from conflict zones"""
        streams = []
        
        # Predefined live streams for conflict zones
        live_streams = [
            {
                "name": "Ukraine War Live",
                "url": "https://www.youtube.com/embed/live_stream?channel=UCX6OQ3DkcsbYNE6H8uQQuVA",
                "thumbnail": "https://img.youtube.com/vi/UCX6OQ3DkcsbYNE6H8uQQuVA/maxresdefault.jpg",
                "location": "Ukraine",
                "coordinates": [30.5234, 50.4501],  # Kyiv
                "type": "conflict_feed",
                "status": "live"
            },
            {
                "name": "Gaza Strip Live",
                "url": "https://www.youtube.com/embed/live_stream?channel=UCPIhBH0e_7HCL-S8o6yoT6Q",
                "thumbnail": "https://img.youtube.com/vi/UCPIhBH0e_7HCL-S8o6yoT6Q/maxresdefault.jpg",
                "location": "Gaza Strip",
                "coordinates": [34.4667, 31.4500],  # Gaza City
                "type": "conflict_feed",
                "status": "live"
            },
            {
                "name": "Israel Border Live",
                "url": "https://www.youtube.com/embed/live_stream?channel=UC4nZ7gVcS0XvZqZxZpZqZQ",
                "thumbnail": "https://img.youtube.com/vi/UC4nZ7gVcS0XvZqZxZpZqZQ/maxresdefault.jpg",
                "location": "Israel-Gaza Border",
                "coordinates": [34.5500, 31.4000],
                "type": "conflict_feed",
                "status": "live"
            }
        ]
        
        for stream in live_streams:
            streams.append({
                "id": f"youtube_{stream['name'].replace(' ', '_')}",
                "type": "live_camera",
                "title": stream["name"],
                "description": f"Live feed from {stream['location']}",
                "url": stream["url"],
                "thumbnail": stream["thumbnail"],
                "location": {
                    "type": "Point",
                    "coordinates": stream["coordinates"]
                },
                "location_name": stream["location"],
                "country": self.extract_country(stream["location"]),
                "feed_type": stream["type"],
                "status": stream["status"],
                "source": "youtube",
                "occurred_at": datetime.now(timezone.utc).isoformat()
            })
        
        return streams
    
    async def fetch_earthcam_feeds(self) -> List[Dict[str, Any]]:
        """Fetch EarthCam feeds from around the world"""
        # Popular EarthCam locations
        earthcam_locations = [
            {
                "name": "Times Square NYC",
                "url": "https://www.earthcam.com/usa/newyork/timessquare/?cam=tsstreet",
                "coordinates": [-73.9855, 40.7580],
                "country": "USA"
            },
            {
                "name": "Tokyo Shibuya Crossing",
                "url": "https://www.skylinewebcams.com/en/webcam/japan/kanto/tokyo/shibuya-crossing.html",
                "coordinates": [139.7000, 35.6595],
                "country": "Japan"
            },
            {
                "name": "London Piccadilly Circus",
                "url": "https://www.skylinewebcams.com/en/webcam/united-kingdom/england/london/piccadilly-circus.html",
                "coordinates": [-0.1340, 51.5099],
                "country": "UK"
            },
            {
                "name": "Eiffel Tower Paris",
                "url": "https://www.skylinewebcams.com/en/webcam/france/ile-de-france/paris/tour-eiffel.html",
                "coordinates": [2.2945, 48.8584],
                "country": "France"
            }
        ]
        
        feeds = []
        for cam in earthcam_locations:
            feeds.append({
                "id": f"earthcam_{cam['name'].replace(' ', '_')}",
                "type": "live_camera",
                "title": f"Live: {cam['name']}",
                "description": f"Live view of {cam['name']}",
                "url": cam["url"],
                "thumbnail": f"https://www.earthcam.com/images/cams/{cam['name'].replace(' ', '')}.jpg",
                "location": {
                    "type": "Point",
                    "coordinates": cam["coordinates"]
                },
                "location_name": cam["name"],
                "country": cam["country"],
                "feed_type": "city_cam",
                "status": "live",
                "source": "earthcam",
                "occurred_at": datetime.now(timezone.utc).isoformat()
            })
        
        return feeds