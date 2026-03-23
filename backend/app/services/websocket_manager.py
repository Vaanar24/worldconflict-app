from fastapi import WebSocket
from typing import List, Dict, Any
import asyncio
import json
from loguru import logger

class WebSocketManager:
    """Manages WebSocket connections and broadcasts real-time events"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_filters: Dict[WebSocket, Dict] = {}
        
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_filters[websocket] = {}
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_filters:
            del self.connection_filters[websocket]
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")
        
    def set_filters(self, websocket: WebSocket, filters: Dict):
        """Set filters for a connection"""
        self.connection_filters[websocket] = filters or {}
        
    async def broadcast_event(self, event: Dict[str, Any]):
        """Broadcast an event to all connected clients that match filters"""
        # Convert event to GeoJSON Feature
        feature = {
            "type": "Feature",
            "geometry": event.get("location"),
            "properties": {k: v for k, v in event.items() if k != "location"}
        }
        
        # Send to each client
        for connection in self.active_connections:
            try:
                # Check if client wants this event based on filters
                filters = self.connection_filters.get(connection, {})
                if self.event_matches_filters(event, filters):
                    await connection.send_json(feature)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                # Remove dead connection
                await self.disconnect(connection)
    
    async def broadcast_many(self, events: List[Dict[str, Any]]):
        """Broadcast multiple events"""
        for event in events:
            await self.broadcast_event(event)
            
    def event_matches_filters(self, event: Dict, filters: Dict) -> bool:
        """Check if an event matches client filters"""
        if not filters:
            return True
            
        # Filter by event type
        if filters.get('event_type') and event.get('type') != filters['event_type']:
            return False
            
        # Filter by threat level
        if filters.get('threat_level') and event.get('threat_level') != filters['threat_level']:
            return False
            
        # Filter by minimum severity
        if filters.get('min_severity') and event.get('severity', 0) < filters['min_severity']:
            return False
            
        # Filter by country
        if filters.get('country') and event.get('country') != filters['country']:
            return False
            
        return True