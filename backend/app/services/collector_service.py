import asyncio
from typing import List, Dict, Any
from datetime import datetime, timezone
from loguru import logger
import os

from app.services.collectors.war_collector import WarEventCollector
from app.services.collectors.gdacs_collector import GDACSCollector

class RealTimeCollector:
    """Main collector service for war and disaster events"""
    
    def __init__(self):
        self.war_collector = WarEventCollector()
        self.gdacs = GDACSCollector()
        self.running = False
        self.collected_events = []
        self.max_events = 2000
        self.event_count = 0
        
    async def start(self):
        """Start all collectors"""
        self.running = True
        logger.info("🚀 Starting World War Monitor collectors...")
        
        # Initial collection
        await self.collect_all()
        
        # Start continuous collection loops
        tasks = [
            self.collect_wars_loop(),
            self.collect_disasters_loop(),
        ]
        
        await asyncio.gather(*tasks)
        
    async def stop(self):
        """Stop all collectors"""
        self.running = False
        logger.info("🛑 Stopping collectors...")
        
    async def collect_all(self):
        """Run all collectors once"""
        logger.info("📡 Running initial collection...")
        
        war_task = self.war_collector.fetch_all_conflicts()
        disaster_task = self.gdacs.fetch_disasters()
        
        war_events, disaster_events = await asyncio.gather(
            war_task, disaster_task, return_exceptions=True
        )
        
        if not isinstance(war_events, Exception):
            for event in war_events:
                await self.add_event(event)
            logger.info(f"✅ Added {len(war_events)} conflict events")
        
        if not isinstance(disaster_events, Exception):
            for event in disaster_events:
                await self.add_event(event)
            logger.info(f"✅ Added {len(disaster_events)} disaster events")
        
        logger.info(f"📊 Total events: {len(self.collected_events)}")
        
    async def collect_wars_loop(self):
        """Collect war events periodically"""
        while self.running:
            try:
                events = await self.war_collector.fetch_all_conflicts()
                for event in events:
                    await self.add_event(event)
                if events:
                    logger.info(f"➕ Added {len(events)} new conflict events")
            except Exception as e:
                logger.error(f"❌ War collection error: {e}")
            
            await asyncio.sleep(300)  # 5 minutes
    
    async def collect_disasters_loop(self):
        """Collect disaster events periodically"""
        while self.running:
            try:
                events = await self.gdacs.fetch_disasters()
                for event in events:
                    await self.add_event(event)
                if events:
                    logger.info(f"➕ Added {len(events)} new disaster events")
            except Exception as e:
                logger.error(f"❌ Disaster collection error: {e}")
            
            await asyncio.sleep(600)  # 10 minutes
    
    async def add_event(self, event: Dict[str, Any]):
        """Add validated event to collection"""
        if not event:
            return
        
        # Check for duplicates
        for existing in self.collected_events:
            if existing.get('source_id') == event.get('source_id'):
                return
        
        # Validate coordinates
        if 'location' in event and 'coordinates' in event['location']:
            coords = event['location']['coordinates']
            if len(coords) >= 2:
                lon, lat = coords[0], coords[1]
                if abs(lat) > 90 or abs(lon) > 180 or (lat == 0 and lon == 0):
                    logger.warning(f"⚠️ Invalid coordinates: {lat}, {lon}")
                    return
            else:
                return
        else:
            return
        
        # Add timestamp
        event['received_at'] = datetime.now(timezone.utc).isoformat()
        
        self.collected_events.append(event)
        self.event_count += 1
        
        # Keep only recent events
        if len(self.collected_events) > self.max_events:
            self.collected_events.sort(
                key=lambda x: x.get('occurred_at', ''), 
                reverse=True
            )
            self.collected_events = self.collected_events[:self.max_events]
        
        logger.info(f"✅ New #{self.event_count}: {event['type']} in {event['country']}")
    
    def get_events_in_bbox(self, min_lon: float, min_lat: float, 
                          max_lon: float, max_lat: float) -> List[Dict]:
        """Get events within bounding box"""
        events_in_bbox = []
        
        for event in self.collected_events:
            coords = event.get('location', {}).get('coordinates', [0, 0])
            if len(coords) >= 2:
                lon, lat = coords[0], coords[1]
                if (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                    events_in_bbox.append(event)
        
        events_in_bbox.sort(key=lambda x: x.get('occurred_at', ''), reverse=True)
        return events_in_bbox
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            "total_events": len(self.collected_events),
            "event_count": self.event_count,
            "running": self.running
        }