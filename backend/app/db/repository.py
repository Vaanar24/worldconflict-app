from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, text
from geoalchemy2.functions import ST_AsGeoJSON, ST_DWithin, ST_MakePoint
import json
from app.models.event import WorldEvent
from app.core.config import get_settings

settings = get_settings()

class EventRepository:
    def __init__(self):
        self.engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=20,
            max_overflow=10
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
    async def create_event(self, event_data: dict) -> WorldEvent:
        """Store event in database"""
        async with self.async_session() as session:
            # Check for duplicate
            existing = await session.execute(
                select(WorldEvent).where(WorldEvent.source_id == event_data['source_id'])
            )
            if existing.scalar_one_or_none():
                return None
                
            event = WorldEvent(
                event_type=event_data['event_type'],
                title=event_data['title'],
                description=event_data['description'],
                location=f"POINT({event_data['location']['coordinates'][0]} {event_data['location']['coordinates'][1]})",
                location_name=event_data.get('location_name'),
                country=event_data.get('country'),
                severity=event_data.get('severity', 0),
                threat_level=event_data.get('threat_level', 'low'),
                occurred_at=event_data['occurred_at'],
                source=event_data['source'],
                source_id=event_data['source_id'],
                raw_data=event_data.get('raw_data', {}),
                metadata=event_data.get('metadata', {})
            )
            
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event
            
    async def get_events_in_bbox(self, min_lon: float, min_lat: float, 
                                  max_lon: float, max_lat: float, 
                                  event_type: str = None, 
                                  limit: int = 1000):
        """Get events within bounding box"""
        async with self.async_session() as session:
            query = select(
                WorldEvent,
                ST_AsGeoJSON(WorldEvent.location).label('geojson')
            ).where(
                WorldEvent.location.intersects(
                    func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
                )
            )
            
            if event_type:
                query = query.where(WorldEvent.event_type == event_type)
                
            query = query.order_by(WorldEvent.occurred_at.desc()).limit(limit)
            
            result = await session.execute(query)
            events = []
            for event, geojson in result:
                event_dict = event.__dict__
                event_dict['location_geojson'] = json.loads(geojson)
                events.append(event_dict)
                
            return events
            
    async def get_events_near_point(self, lon: float, lat: float, 
                                     radius_km: float = 50, 
                                     limit: int = 100):
        """Find events near a specific point"""
        async with self.async_session() as session:
            # Convert radius from km to degrees (approximate)
            radius_deg = radius_km / 111.0
            
            query = select(WorldEvent).where(
                ST_DWithin(
                    WorldEvent.location,
                    ST_MakePoint(lon, lat),
                    radius_deg
                )
            ).order_by(WorldEvent.occurred_at.desc()).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()