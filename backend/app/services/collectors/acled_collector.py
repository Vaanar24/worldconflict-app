import aiohttp
import asyncio
from datetime import datetime, timedelta
from app.services.kafka_service import kafka_service
from app.core.config import get_settings
from loguru import logger

settings = get_settings()

class ACLEDCollector:
    """Collects conflict data from ACLED API"""
    
    def __init__(self):
        self.api_url = "https://api.acleddata.com/acled/read"
        self.api_key = settings.acled_api_key
        self.running = False
        
    async def start_collection(self, interval_minutes=5):
        """Periodically fetch ACLED data"""
        self.running = True
        while self.running:
            try:
                await self.collect_events()
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                logger.error(f"ACLED collection error: {e}")
                await asyncio.sleep(60)
                
    async def collect_events(self):
        """Fetch recent conflict events"""
        # Get events from last 24 hours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        params = {
            'key': self.api_key,
            'email': 'your-email@example.com',
            'event_date': f"{start_date.strftime('%Y-%m-%d')}|{end_date.strftime('%Y-%m-%d')}",
            'fields': 'event_id_cnty,event_date,event_type,country,admin1,admin2,location,latitude,longitude,fatalities,notes',
            'limit': 1000,
            'export_format': 'json'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for event in data.get('data', []):
                        await self.process_event(event)
                        
    async def process_event(self, raw_event):
        """Transform and send to Kafka"""
        processed_event = {
            'source': 'acled',
            'source_id': raw_event.get('event_id_cnty'),
            'event_type': 'conflict',
            'title': f"{raw_event.get('event_type')} in {raw_event.get('location')}",
            'description': raw_event.get('notes', '')[:2000],
            'location': {
                'type': 'Point',
                'coordinates': [float(raw_event.get('longitude', 0)), float(raw_event.get('latitude', 0))]
            },
            'location_name': raw_event.get('location'),
            'country': raw_event.get('country'),
            'severity': min(float(raw_event.get('fatalities', 0)) / 10, 10),
            'threat_level': self.calculate_threat_level(raw_event),
            'occurred_at': raw_event.get('event_date'),
            'raw_data': raw_event,
            'metadata': {
                'event_type': raw_event.get('event_type'),
                'fatalities': raw_event.get('fatalities'),
                'admin1': raw_event.get('admin1'),
                'admin2': raw_event.get('admin2')
            }
        }
        
        await kafka_service.produce_event('conflict', processed_event)
        
    def calculate_threat_level(self, event):
        fatalities = int(event.get('fatalities', 0))
        if fatalities > 10:
            return 'critical'
        elif fatalities > 3:
            return 'high'
        elif fatalities > 0:
            return 'medium'
        return 'low'