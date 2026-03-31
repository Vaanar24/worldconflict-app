from fastapi import APIRouter, Query, Request
from datetime import datetime, timedelta, timezone
from typing import Optional
from loguru import logger
from app.services.historical_service import historical_service

router = APIRouter(prefix="/historical", tags=["historical"])

@router.get("/conflict-trends")
async def get_conflict_trends(
    days: int = Query(90, ge=1, le=365),
    granularity: str = Query("day", regex="^(day|week|month)$")
):
    """Get conflict trend data for visualization"""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    logger.info(f"Fetching conflict trends: days={days}, granularity={granularity}")
    trends = historical_service.get_conflict_trends(start_date, end_date, granularity)
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "granularity": granularity,
        "data": trends
    }

@router.get("/casualty-trends")
async def get_casualty_trends(
    days: int = Query(90, ge=1, le=365),
    include_civilian: bool = Query(True)
):
    """Get casualty trend data"""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    logger.info(f"Fetching casualty trends: days={days}")
    casualties = historical_service.get_casualty_trends(start_date, end_date)
    
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_casualties": sum(c["total_casualties"] for c in casualties),
        "data": casualties
    }

@router.get("/territorial-changes")
async def get_territorial_changes():
    """Get territorial changes data"""
    changes = historical_service.get_territorial_changes()
    logger.info(f"Fetching territorial changes: {len(changes)} found")
    
    return {
        "total_changes": len(changes),
        "changes": changes
    }

@router.get("/heatmap")
async def get_heatmap_data(
    bbox: str = Query(..., description="min_lon,min_lat,max_lon,max_lat")
):
    """Get heatmap intensity data for map view"""
    try:
        coords = [float(x) for x in bbox.split(',')]
        min_lon, min_lat, max_lon, max_lat = coords
    except:
        min_lon, min_lat, max_lon, max_lat = -180, -90, 180, 90
    
    logger.info(f"Fetching heatmap data for bbox: {bbox}")
    heatmap_data = historical_service.generate_heatmap_data(
        min_lon, min_lat, max_lon, max_lat
    )
    
    return {
        "type": "Heatmap",
        "data": heatmap_data
    }

@router.get("/statistics")
async def get_historical_statistics(days: int = Query(90)):
    """Get summary statistics for historical period"""
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    conflicts = historical_service.get_conflict_trends(start_date, end_date)
    casualties = historical_service.get_casualty_trends(start_date, end_date)
    
    total_events = sum(c["event_count"] for c in conflicts)
    
    return {
        "period_days": days,
        "summary": {
            "total_events": total_events,
            "avg_daily_events": round(total_events / days, 1) if days > 0 else 0,
            "total_casualties": sum(c["total_casualties"] for c in casualties),
            "peak_event_day": max(conflicts, key=lambda x: x["event_count"])["timestamp"] if conflicts else None,
            "peak_event_count": max(c["event_count"] for c in conflicts) if conflicts else 0
        }
    }