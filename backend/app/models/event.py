from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class EventType(str, Enum):
    CONFLICT = "conflict"
    BATTLE = "battle"
    AIR_STRIKE = "air_strike"
    ARTILLERY = "artillery"
    GROUND_ASSAULT = "ground_assault"
    CEASEFIRE = "ceasefire"
    PEACE_TALKS = "peace_talks"
    TROOP_MOVEMENT = "troop_movement"
    CIVILIAN_CASUALTY = "civilian_casualty"
    MILITARY_CASUALTY = "military_casualty"
    TERRITORY_CHANGE = "territory_change"
    SANCTIONS = "sanctions"
    DIPLOMATIC = "diplomatic"
    EARTHQUAKE = "earthquake"
    STORM = "storm"
    FLOOD = "flood"

class ThreatLevel(str, Enum):
    CRITICAL = "critical"      # Active war zone, heavy fighting
    HIGH = "high"               # Active conflict, sporadic fighting
    MEDIUM = "medium"           # Tensions high, skirmishes
    LOW = "low"                 # Monitoring, post-conflict
    CEASEFIRE = "ceasefire"     # Ceasefire in effect

class Location(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude]

class Casualties(BaseModel):
    military: Optional[int] = None
    civilian: Optional[int] = None
    total: Optional[int] = None
    source: Optional[str] = None

class ConflictDetails(BaseModel):
    parties_involved: List[str] = []
    front_line: Optional[str] = None
    strategic_importance: Optional[str] = None
    civilian_impact: Optional[str] = None
    infrastructure_damage: Optional[str] = None

class Event(BaseModel):
    id: str
    type: EventType
    title: str
    description: str
    location: Location
    location_name: str
    country: str
    region: str = "Unknown"
    severity: float = Field(ge=0, le=10)
    threat_level: ThreatLevel
    casualties: Optional[Casualties] = None
    conflict_details: Optional[ConflictDetails] = None
    occurred_at: datetime
    source: str
    source_id: str
    verified: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EventFeature(BaseModel):
    type: str = "Feature"
    geometry: Location
    properties: Event

class EventCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[EventFeature]