from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge
import time

router = APIRouter(prefix="/metrics", tags=["monitoring"])

# Define metrics
events_received = Counter('events_received_total', 'Total events received', ['type'])
events_processed = Counter('events_processed_total', 'Total events processed', ['status'])
processing_duration = Histogram('event_processing_seconds', 'Event processing duration', ['type'])
active_connections = Gauge('websocket_active_connections', 'Active WebSocket connections')
api_requests = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])

@router.get("/")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# Middleware to track metrics
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    api_requests.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response