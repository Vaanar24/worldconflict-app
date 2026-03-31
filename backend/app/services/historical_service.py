import random
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from collections import defaultdict
import numpy as np
from loguru import logger

class HistoricalDataService:
    """Service for generating and managing historical conflict data"""
    
    def __init__(self):
        self.conflict_history = []
        self.casualty_history = []
        self.territorial_changes = []
        self._generate_mock_historical_data()
        logger.info("HistoricalDataService initialized with mock data")
    
    def _generate_mock_historical_data(self):
        """Generate realistic mock historical data for visualization"""
        now = datetime.now(timezone.utc)
        
        # Generate conflict trends for last 12 months
        for days_ago in range(365, -1, -1):
            timestamp = now - timedelta(days=days_ago)
            
            # Simulate conflict intensity (higher in recent months)
            intensity = 0.3 + (days_ago / 365) * 0.5 + random.uniform(-0.1, 0.1)
            if days_ago < 60:  # Last 2 months more intense
                intensity += 0.3
            elif days_ago < 180:  # 6 months ago
                intensity += 0.2
            
            event_count = int(50 * intensity + random.randint(-10, 20))
            active_conflicts = int(15 * intensity + random.randint(-3, 5))
            
            # Simulate major events (spikes)
            if days_ago == 30:  # Escalation
                event_count = 120
                active_conflicts = 25
            elif days_ago == 90:  # Ceasefire attempt
                event_count = 35
                active_conflicts = 12
            elif days_ago == 180:  # Major offensive
                event_count = 150
                active_conflicts = 28
            
            self.conflict_history.append({
                "timestamp": timestamp.isoformat(),
                "event_count": max(0, event_count),
                "severity_avg": round(min(8.5, max(3, intensity * 8)), 1),
                "threat_level_distribution": {
                    "critical": int(event_count * 0.3),
                    "high": int(event_count * 0.4),
                    "medium": int(event_count * 0.2),
                    "low": int(event_count * 0.1)
                },
                "active_conflicts": max(5, active_conflicts)
            })
        
        # Generate casualty trends
        for days_ago in range(365, -1, -1):
            timestamp = now - timedelta(days=days_ago)
            
            base_casualties = 500 + (days_ago / 365) * 800
            if days_ago < 60:
                base_casualties *= 1.5
            
            military = int(base_casualties * 0.6 + random.randint(-50, 100))
            civilian = int(base_casualties * 0.4 + random.randint(-30, 70))
            
            self.casualty_history.append({
                "timestamp": timestamp.isoformat(),
                "military_casualties": max(0, military),
                "civilian_casualties": max(0, civilian),
                "total_casualties": max(0, military + civilian),
                "source": "estimated"
            })
        
        # Generate territorial changes
        self.territorial_changes = [
            {
                "id": "ukr_kharkiv_2024",
                "location_name": "Kharkiv Region",
                "country": "Ukraine",
                "from_control": "Ukraine",
                "to_control": "Russia",
                "changed_at": (now - timedelta(days=45)).isoformat(),
                "coordinates": [36.25, 49.98],
                "significance": "strategic",
                "source": "ISW"
            },
            {
                "id": "ukr_bakhmut_2024",
                "location_name": "Bakhmut",
                "country": "Ukraine",
                "from_control": "Ukraine",
                "to_control": "Russia",
                "changed_at": (now - timedelta(days=120)).isoformat(),
                "coordinates": [38.0, 48.6],
                "significance": "strategic",
                "source": "ISW"
            },
            {
                "id": "gaza_north_2024",
                "location_name": "Northern Gaza",
                "country": "Palestine",
                "from_control": "Hamas",
                "to_control": "IDF",
                "changed_at": (now - timedelta(days=30)).isoformat(),
                "coordinates": [34.5, 31.55],
                "significance": "tactical",
                "source": "UN OCHA"
            },
            {
                "id": "sudan_khartoum_2024",
                "location_name": "Khartoum",
                "country": "Sudan",
                "from_control": "RSF",
                "to_control": "SAF",
                "changed_at": (now - timedelta(days=15)).isoformat(),
                "coordinates": [32.55, 15.5],
                "significance": "strategic",
                "source": "ACLED"
            },
            {
                "id": "myanmar_kachin_2024",
                "location_name": "Kachin State",
                "country": "Myanmar",
                "from_control": "Tatmadaw",
                "to_control": "KIA",
                "changed_at": (now - timedelta(days=60)).isoformat(),
                "coordinates": [97.35, 26.0],
                "significance": "tactical",
                "source": "ACLED"
            }
        ]
        logger.info(f"Generated {len(self.conflict_history)} conflict records, {len(self.casualty_history)} casualty records")
    
    def get_conflict_trends(self, start_date: datetime, end_date: datetime, 
                           granularity: str = "day") -> List[Dict]:
        """Get conflict trend data for specified time range"""
        # Filter data
        filtered = []
        for d in self.conflict_history:
            try:
                d_time = datetime.fromisoformat(d["timestamp"])
                if start_date <= d_time <= end_date:
                    filtered.append(d)
            except:
                continue
        
        if granularity == "week":
            return self._aggregate_by_week(filtered)
        elif granularity == "month":
            return self._aggregate_by_month(filtered)
        return filtered
    
    def get_casualty_trends(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get casualty trend data"""
        filtered = []
        for d in self.casualty_history:
            try:
                d_time = datetime.fromisoformat(d["timestamp"])
                if start_date <= d_time <= end_date:
                    filtered.append(d)
            except:
                continue
        return filtered
    
    def get_territorial_changes(self) -> List[Dict]:
        """Get all territorial changes"""
        return self.territorial_changes
    
    def generate_heatmap_data(self, min_lon: float, min_lat: float,
                               max_lon: float, max_lat: float) -> List[Dict]:
        """Generate heatmap intensity data for current view"""
        heatmap_points = []
        
        # Generate points for major conflict zones
        conflict_zones = [
            {"coords": [30.5, 50.5], "intensity": 95, "radius": 150},  # Ukraine
            {"coords": [34.5, 31.5], "intensity": 90, "radius": 80},   # Gaza
            {"coords": [32.5, 15.5], "intensity": 85, "radius": 200},   # Sudan
            {"coords": [96.5, 22.0], "intensity": 80, "radius": 180},   # Myanmar
            {"coords": [29.0, -1.5], "intensity": 75, "radius": 250},    # DR Congo
            {"coords": [39.5, 13.5], "intensity": 70, "radius": 150},    # Ethiopia
            {"coords": [-72.5, 18.5], "intensity": 65, "radius": 80},    # Haiti
            {"coords": [44.5, 12.5], "intensity": 60, "radius": 100},    # Yemen
            {"coords": [70.5, 34.5], "intensity": 55, "radius": 120},    # Afghanistan
            {"coords": [44.0, 33.0], "intensity": 50, "radius": 100},    # Iraq
        ]
        
        for zone in conflict_zones:
            if (min_lon <= zone["coords"][0] <= max_lon and 
                min_lat <= zone["coords"][1] <= max_lat):
                heatmap_points.append({
                    "coordinates": zone["coords"],
                    "intensity": zone["intensity"],
                    "radius": zone["radius"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "event_type": "conflict"
                })
        
        return heatmap_points
    
    def _aggregate_by_week(self, data: List[Dict]) -> List[Dict]:
        """Aggregate daily data into weekly"""
        weekly = defaultdict(lambda: {"event_count": 0, "severity_sum": 0, "count": 0, "active_conflicts_sum": 0})
        
        for d in data:
            d_time = datetime.fromisoformat(d["timestamp"])
            week_key = d_time.strftime("%Y-W%W")
            weekly[week_key]["event_count"] += d["event_count"]
            weekly[week_key]["severity_sum"] += d["severity_avg"]
            weekly[week_key]["active_conflicts_sum"] += d["active_conflicts"]
            weekly[week_key]["count"] += 1
            if "timestamp" not in weekly[week_key]:
                weekly[week_key]["timestamp"] = d["timestamp"]
        
        result = []
        for key, value in weekly.items():
            result.append({
                "timestamp": value["timestamp"],
                "event_count": value["event_count"],
                "severity_avg": round(value["severity_sum"] / value["count"], 1),
                "active_conflicts": int(value["active_conflicts_sum"] / value["count"])
            })
        
        return sorted(result, key=lambda x: x["timestamp"])
    
    def _aggregate_by_month(self, data: List[Dict]) -> List[Dict]:
        """Aggregate daily data into monthly"""
        monthly = defaultdict(lambda: {"event_count": 0, "severity_sum": 0, "count": 0, "active_conflicts_sum": 0})
        
        for d in data:
            d_time = datetime.fromisoformat(d["timestamp"])
            month_key = d_time.strftime("%Y-%m")
            monthly[month_key]["event_count"] += d["event_count"]
            monthly[month_key]["severity_sum"] += d["severity_avg"]
            monthly[month_key]["active_conflicts_sum"] += d["active_conflicts"]
            monthly[month_key]["count"] += 1
            if "timestamp" not in monthly[month_key]:
                monthly[month_key]["timestamp"] = d["timestamp"]
        
        result = []
        for key, value in monthly.items():
            result.append({
                "timestamp": value["timestamp"],
                "event_count": value["event_count"],
                "severity_avg": round(value["severity_sum"] / value["count"], 1),
                "active_conflicts": int(value["active_conflicts_sum"] / value["count"])
            })
        
        return sorted(result, key=lambda x: x["timestamp"])

# Create a singleton instance
historical_service = HistoricalDataService()