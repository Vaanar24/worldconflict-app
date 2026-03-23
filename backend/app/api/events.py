from fastapi import APIRouter, Query, Request
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.models.event import Event, EventCollection, EventFeature

router = APIRouter(prefix="/events", tags=["events"])

@router.get("/", response_model=EventCollection)
async def get_events(
    request: Request,
    bbox: str = Query(..., description="min_lon,min_lat,max_lon,max_lat"),
    event_type: Optional[str] = None,
    threat_level: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(1000, ge=1, le=1000)
):
    """Get war and conflict events"""
    try:
        coords = [float(x) for x in bbox.split(',')]
        min_lon, min_lat, max_lon, max_lat = coords
    except:
        min_lon, min_lat, max_lon, max_lat = -180, -90, 180, 90
    
    collector = request.app.state.collector
    raw_events = collector.get_events_in_bbox(min_lon, min_lat, max_lon, max_lat)
    
    features = []
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    for event_data in raw_events:
        # Time filter
        occurred_at = datetime.fromisoformat(event_data['occurred_at'].replace('Z', '+00:00'))
        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)
        
        if occurred_at < cutoff_time:
            continue
        
        # Type filter
        if event_type and event_data.get('type') != event_type:
            continue
        
        # Threat filter
        if threat_level and event_data.get('threat_level') != threat_level:
            continue
        
        try:
            event = Event(**event_data)
            feature = EventFeature(
                geometry=event.location,
                properties=event
            )
            features.append(feature)
        except:
            continue
    
    return EventCollection(features=features[:limit])

@router.get("/stats")
async def get_stats(request: Request, hours: int = 24):
    """Get war statistics"""
    collector = request.app.state.collector
    events = collector.collected_events
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    recent_events = []
    
    for event in events:
        occurred_at = datetime.fromisoformat(event['occurred_at'].replace('Z', '+00:00'))
        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)
        
        if occurred_at >= cutoff_time:
            recent_events.append(event)
    
    # Calculate statistics
    by_type = {}
    by_threat = {}
    countries = {}
    total_casualties = 0
    
    for event in recent_events:
        e_type = event.get('type', 'unknown')
        by_type[e_type] = by_type.get(e_type, 0) + 1
        
        threat = event.get('threat_level', 'unknown')
        by_threat[threat] = by_threat.get(threat, 0) + 1
        
        country = event.get('country', 'Unknown')
        countries[country] = countries.get(country, 0) + 1
        
        if event.get('casualties'):
            total_casualties += event['casualties'].get('total', 0)
    
    hotspots = [{"country": k, "count": v} for k, v in countries.items()]
    hotspots.sort(key=lambda x: x['count'], reverse=True)
    
    return {
        "total_events": len(recent_events),
        "total_casualties": total_casualties,
        "active_conflicts": by_type.get('conflict', 0) + by_type.get('battle', 0),
        "by_type": by_type,
        "by_threat_level": by_threat,
        "hotspots": hotspots[:10]
    }