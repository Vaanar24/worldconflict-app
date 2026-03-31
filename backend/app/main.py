from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import events, cameras, historical
from app.core.config import get_settings
from app.services.collector_service import RealTimeCollector

settings = get_settings()
collector = RealTimeCollector()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting World War Monitor API...")
    asyncio.create_task(collector.start())
    yield
    logger.info("🛑 Shutting down...")
    await collector.stop()

def create_application() -> FastAPI:
    app = FastAPI(
        title="World War Monitor",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.state.collector = collector
    app.include_router(events.router, prefix=settings.api_prefix)
    app.include_router(cameras.router, prefix=settings.api_prefix)
    app.include_router(historical.router, prefix=settings.api_prefix)
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "events_collected": len(collector.collected_events),
            "running": collector.running
        }
    
    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)