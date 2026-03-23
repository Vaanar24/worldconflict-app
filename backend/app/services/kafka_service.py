from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from app.core.config import get_settings
import json
import asyncio
from typing import Dict, Any, Callable
from loguru import logger

settings = get_settings()

class KafkaService:
    def __init__(self):
        self.producer = None
        self.consumer = None
        self._running = False
        self._handlers = {}
        
    async def start(self):
        """Initialize Kafka producer and consumer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()
        logger.info("Kafka producer started")
        
    async def stop(self):
        """Clean shutdown"""
        if self.producer:
            await self.producer.stop()
        if self.consumer:
            await self.consumer.stop()
            
    async def produce_event(self, event_type: str, event_data: Dict[str, Any]):
        """Send event to Kafka topic"""
        try:
            message = {
                'type': event_type,
                'data': event_data,
                'timestamp': event_data.get('timestamp')
            }
            await self.producer.send(
                settings.kafka_events_topic,
                value=message,
                key=event_data.get('source_id', '').encode()
            )
            logger.debug(f"Produced event: {event_type}")
        except Exception as e:
            logger.error(f"Kafka produce error: {e}")
            
    async def start_consumer(self, handler: Callable):
        """Start consuming messages from Kafka"""
        self.consumer = AIOKafkaConsumer(
            settings.kafka_events_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id=settings.kafka_consumer_group,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='latest'
        )
        await self.consumer.start()
        self._running = True
        
        try:
            async for msg in self.consumer:
                if not self._running:
                    break
                await handler(msg.value)
        finally:
            await self.consumer.stop()
            
    def is_healthy(self):
        return self.producer is not None and not self.producer._closed