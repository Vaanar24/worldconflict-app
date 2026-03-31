from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

class TimeGranularity(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class ConflictTrend(BaseModel):
    timestamp: datetime
    event_count: int
    severity_avg: float
    threat_level_distribution: Dict[str, int]
    active_conflicts: int

class CasualtyTrend(BaseModel):
    timestamp: datetime
    military_casualties: int
    civilian_casualties: int
    total_casualties: int
    source: str

class TerritorialChange(BaseModel):
    id: str
    location_name: str
    country: str
    from_control: str
    to_control: str
    changed_at: datetime
    coordinates: List[float]
    significance: str  # strategic, symbolic, tactical
    source: str

class HeatmapData(BaseModel):
    coordinates: List[float]  # [lon, lat]
    intensity: float  # 0-100 based on conflict severity
    radius: int  # in km
    timestamp: datetime
    event_type: str