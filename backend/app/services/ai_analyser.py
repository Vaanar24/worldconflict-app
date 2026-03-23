from transformers import pipeline
import numpy as np
from typing import Dict, Any

class AIEventAnalyzer:
    def __init__(self):
        # Initialize ML models
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
    async def analyze_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add AI-powered insights to events"""
        text = f"{event['title']} {event.get('description', '')}"
        
        # Classify event type if not already classified
        if not event.get('event_type'):
            candidates = ['conflict', 'natural disaster', 'protest', 'diplomatic event', 'economic']
            result = self.classifier(text, candidates)
            event['ai_classification'] = result['labels'][0]
            event['ai_confidence'] = result['scores'][0]
        
        # Analyze sentiment
        sentiment = self.sentiment_analyzer(text[:512])[0]
        event['sentiment'] = {
            'label': sentiment['label'],
            'score': sentiment['score']
        }
        
        # Generate threat score
        event['ai_threat_score'] = self.calculate_threat_score(event)
        
        return event
    
    def calculate_threat_score(self, event):
        """Calculate threat score based on multiple factors"""
        score = 0.0
        
        # Base score from severity
        score += event.get('severity', 5) * 0.3
        
        # Adjust by sentiment
        if event.get('sentiment', {}).get('label') == 'NEGATIVE':
            score += 2.0
            
        # Event type weighting
        weights = {
            'conflict': 3.0,
            'earthquake': 2.5,
            'unrest': 2.0,
            'news': 1.0
        }
        score += weights.get(event.get('event_type'), 1.0)
        
        return min(10.0, score)