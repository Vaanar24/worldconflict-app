from fastapi import APIRouter, Request
from typing import List, Dict, Any
from datetime import datetime, timezone
from loguru import logger

router = APIRouter(prefix="/cameras", tags=["cameras"])

# Working camera feeds with proper embed URLs
CAMERA_FEEDS = [
    {
        "id": "ukraine_kyiv",
        "title": "Ukraine - Kyiv City Center",
        "description": "Live webcam view of Independence Square (Maidan Nezalezhnosti), Kyiv",
        "url": "https://www.youtube.com/embed/SlHjBp_w4kA",
        "thumbnail": "https://img.youtube.com/vi/SlHjBp_w4kA/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [30.5234, 50.4501]},
        "location_name": "Kyiv",
        "country": "Ukraine",
        "feed_type": "conflict_feed",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "israel_jerusalem",
        "title": "Jerusalem - Western Wall",
        "description": "Live view of the Western Wall, Jerusalem",
        "url": "https://www.youtube.com/embed/ZN5jW6G-qOk",
        "thumbnail": "https://img.youtube.com/vi/ZN5jW6G-qOk/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [35.2332, 31.7767]},
        "location_name": "Jerusalem",
        "country": "Israel",
        "feed_type": "conflict_feed",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "gaza_beach",
        "title": "Gaza Beach View",
        "description": "Live view of Gaza Beach and Mediterranean Sea",
        "url": "https://www.youtube.com/embed/7jLvJwXq8QY",
        "thumbnail": "https://img.youtube.com/vi/7jLvJwXq8QY/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [34.4667, 31.4500]},
        "location_name": "Gaza City",
        "country": "Palestine",
        "feed_type": "conflict_feed",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "new_york_times_square",
        "title": "New York - Times Square",
        "description": "Live view of Times Square, New York City",
        "url": "https://www.youtube.com/embed/1hJGh9BRNDM",
        "thumbnail": "https://img.youtube.com/vi/1hJGh9BRNDM/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [-73.9855, 40.7580]},
        "location_name": "Times Square",
        "country": "USA",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "tokyo_shibuya",
        "title": "Tokyo - Shibuya Crossing",
        "description": "Live view of the famous Shibuya Crossing",
        "url": "https://www.youtube.com/embed/FQHtKJ7YXZI",
        "thumbnail": "https://img.youtube.com/vi/FQHtKJ7YXZI/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [139.7000, 35.6595]},
        "location_name": "Shibuya",
        "country": "Japan",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "london_piccadilly",
        "title": "London - Piccadilly Circus",
        "description": "Live view of Piccadilly Circus, London",
        "url": "https://www.youtube.com/embed/irv1YGgQXeg",
        "thumbnail": "https://img.youtube.com/vi/irv1YGgQXeg/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [-0.1340, 51.5099]},
        "location_name": "Piccadilly Circus",
        "country": "UK",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "paris_eiffel",
        "title": "Paris - Eiffel Tower",
        "description": "Live view of the Eiffel Tower, Paris",
        "url": "https://www.youtube.com/embed/46sQ0OMlV-U",
        "thumbnail": "https://img.youtube.com/vi/46sQ0OMlV-U/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [2.2945, 48.8584]},
        "location_name": "Eiffel Tower",
        "country": "France",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "dubai_fountain",
        "title": "Dubai - Burj Khalifa & Fountain",
        "description": "Live view of Burj Khalifa and Dubai Fountain",
        "url": "https://www.youtube.com/embed/UrBkfR_Hq28",
        "thumbnail": "https://img.youtube.com/vi/UrBkfR_Hq28/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [55.2742, 25.1972]},
        "location_name": "Burj Khalifa",
        "country": "UAE",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "sydney_opera",
        "title": "Sydney - Opera House",
        "description": "Live view of Sydney Opera House and Harbour Bridge",
        "url": "https://www.youtube.com/embed/hbfVJotXf7A",
        "thumbnail": "https://img.youtube.com/vi/hbfVJotXf7A/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [151.2153, -33.8568]},
        "location_name": "Sydney Opera House",
        "country": "Australia",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "rio_copacabana",
        "title": "Rio de Janeiro - Copacabana Beach",
        "description": "Live view of Copacabana Beach",
        "url": "https://www.youtube.com/embed/FjCgqYcIY0I",
        "thumbnail": "https://img.youtube.com/vi/FjCgqYcIY0I/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [-43.1729, -22.9068]},
        "location_name": "Copacabana Beach",
        "country": "Brazil",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "cape_town_table",
        "title": "Cape Town - Table Mountain",
        "description": "Live view of Table Mountain, Cape Town",
        "url": "https://www.youtube.com/embed/8E7h3QqZtY8",
        "thumbnail": "https://img.youtube.com/vi/8E7h3QqZtY8/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [18.4241, -33.9249]},
        "location_name": "Table Mountain",
        "country": "South Africa",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "moscow_red_square",
        "title": "Moscow - Red Square",
        "description": "Live view of Red Square and St. Basil's Cathedral",
        "url": "https://www.youtube.com/embed/l8vUJfNw0-Y",
        "thumbnail": "https://img.youtube.com/vi/l8vUJfNw0-Y/maxresdefault.jpg",
        "location": {"type": "Point", "coordinates": [37.6173, 55.7558]},
        "location_name": "Red Square",
        "country": "Russia",
        "feed_type": "city_cam",
        "status": "live",
        "source": "youtube",
        "occurred_at": datetime.now(timezone.utc).isoformat()
    }
]

@router.get("/")
async def get_camera_feeds(request: Request, location: str = None, feed_type: str = None):
    """Get available live camera feeds"""
    feeds = CAMERA_FEEDS.copy()
    
    # Filter by location
    if location:
        feeds = [f for f in feeds if location.lower() in f['location_name'].lower() or location.lower() in f['country'].lower()]
    
    # Filter by feed type
    if feed_type:
        feeds = [f for f in feeds if f['feed_type'] == feed_type]
    
    return {
        "total": len(feeds),
        "feeds": feeds
    }

@router.get("/nearby")
async def get_nearby_cameras(request: Request, lat: float, lng: float, radius_km: float = 100):
    """Get cameras near a specific location"""
    feeds = CAMERA_FEEDS.copy()
    
    nearby = []
    for feed in feeds:
        feed_lat = feed['location']['coordinates'][1]
        feed_lng = feed['location']['coordinates'][0]
        
        # Approximate distance using Haversine formula (simplified)
        distance = ((feed_lat - lat) ** 2 + (feed_lng - lng) ** 2) ** 0.5 * 111
        if distance <= radius_km:
            nearby.append(feed)
    
    return {
        "location": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "cameras": nearby
    }