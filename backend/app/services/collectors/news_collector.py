import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os
from loguru import logger

class NewsCollector:
    """Collects real-time news events from NewsAPI"""
    
    def __init__(self, api_key: str = None):
        # Try to get from param, then env var
        self.api_key = api_key or os.getenv('NEWS_API_KEY', '')
        self.base_url = "https://newsapi.org/v2"
        self.source = "newsapi"
        
        if self.api_key:
            logger.info(f"NewsAPI collector initialized with API key: {self.api_key[:5]}...")
        else:
            logger.warning("No NewsAPI key provided, news collection will be skipped")
    
    # FIX: Method name should be fetch_breaking_news (not fetch_breaking_news)
    async def fetch_breaking_news(self, minutes: int = 30) -> List[Dict[str, Any]]:
        """Fetch breaking news"""
        if not self.api_key:
            logger.warning("No NewsAPI key provided, skipping news collection")
            return []
            
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes)
        
        params = {
            'apiKey': self.api_key,
            'language': 'en',
            'pageSize': 50,
            'sortBy': 'publishedAt',
            'from': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'to': end_time.strftime('%Y-%m-%dT%H:%M:%S')
        }
        
        # Keywords that might indicate significant events
        keywords = ['earthquake', 'protest', 'conflict', 'attack', 'explosion', 
                   'eruption', 'flood', 'storm', 'wildfire', 'pandemic', 'crisis']
        
        all_events = []
        
        for keyword in keywords:
            params['q'] = keyword
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/everything", 
                                         params=params, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            articles = data.get('articles', [])
                            events = await self.process_articles(articles, keyword)
                            all_events.extend(events)
                            logger.info(f"Fetched {len(articles)} news articles for '{keyword}'")
                        else:
                            logger.error(f"NewsAPI error: {response.status}")
            except Exception as e:
                logger.error(f"Error fetching news for '{keyword}': {e}")
                continue
                
        return all_events
    
    async def process_articles(self, articles: List[Dict], keyword: str) -> List[Dict]:
        """Process news articles into our event format"""
        events = []
        
        for article in articles:
            try:
                # Skip articles without location info
                if not article.get('title') or not article.get('description'):
                    continue
                
                # Try to extract location from title or description
                location_info = self.extract_location(article['title'] + ' ' + article['description'])
                
                # If we can't find a location, use a default or skip
                if not location_info['country']:
                    # Use a simple geocoding approach or default to world
                    location_info['country'] = 'Global'
                    location_info['coordinates'] = [0, 20]  # Default center
                
                # Calculate severity based on keyword and source credibility
                severity = self.calculate_severity(keyword, article)
                
                # Determine threat level
                threat_level = self.determine_threat_level(keyword, severity)
                
                # Parse timestamp
                published_at = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                
                event = {
                    'id': f"news_{hash(article['url'])}",
                    'type': 'news',
                    'title': article['title'][:200],
                    'description': article['description'][:500] if article['description'] else '',
                    'location': {
                        'type': 'Point',
                        'coordinates': location_info['coordinates']
                    },
                    'location_name': location_info['city'] or location_info['country'],
                    'country': location_info['country'],
                    'severity': severity,
                    'threat_level': threat_level,
                    'occurred_at': published_at.isoformat(),
                    'source': self.source,
                    'source_id': article['url'],
                    'metadata': {
                        'keyword': keyword,
                        'source_name': article.get('source', {}).get('name', 'Unknown'),
                        'author': article.get('author'),
                        'url': article['url'],
                        'image_url': article.get('urlToImage')
                    }
                }
                events.append(event)
                
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                continue
                
        return events
    
    def extract_location(self, text: str) -> Dict:
        """Simple location extraction from text"""
        # This is a simplified version - in production, use a proper geocoding service
        countries = {
            'USA': ['usa', 'united states', 'america', 'new york', 'washington', 'california'],
            'UK': ['uk', 'united kingdom', 'london', 'england', 'britain'],
            'France': ['france', 'paris'],
            'Germany': ['germany', 'berlin'],
            'Japan': ['japan', 'tokyo'],
            'China': ['china', 'beijing', 'shanghai'],
            'Russia': ['russia', 'moscow'],
            'India': ['india', 'mumbai', 'delhi'],
            'Brazil': ['brazil', 'rio', 'brasilia'],
            'Australia': ['australia', 'sydney', 'melbourne'],
        }
        
        text_lower = text.lower()
        
        for country, keywords in countries.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Approximate coordinates (simplified - use geocoding in production)
                    coords = self.get_country_coordinates(country)
                    return {
                        'country': country,
                        'city': keyword.title(),
                        'coordinates': coords
                    }
        
        return {
            'country': 'Global',
            'city': None,
            'coordinates': [0, 20]
        }
    
    def get_country_coordinates(self, country: str) -> List[float]:
        """Get approximate coordinates for a country"""
        coordinates = {
            'USA': [-98.5795, 39.8283],
            'UK': [-3.4360, 55.3781],
            'France': [2.2137, 46.6034],
            'Germany': [10.4515, 51.1657],
            'Japan': [138.2529, 36.2048],
            'China': [104.1954, 35.8617],
            'Russia': [105.3188, 61.5240],
            'India': [78.9629, 20.5937],
            'Brazil': [-51.9253, -14.2350],
            'Australia': [133.7751, -25.2744],
        }
        return coordinates.get(country, [0, 20])
    
    def calculate_severity(self, keyword: str, article: Dict) -> float:
        """Calculate event severity based on keyword and article"""
        base_scores = {
            'earthquake': 7.0,
            'conflict': 8.0,
            'attack': 9.0,
            'explosion': 8.5,
            'eruption': 7.5,
            'flood': 6.0,
            'storm': 5.0,
            'wildfire': 6.5,
            'pandemic': 8.0,
            'crisis': 7.0,
            'protest': 5.0
        }
        
        score = base_scores.get(keyword, 5.0)
        
        # Adjust based on source credibility (simplified)
        source = article.get('source', {}).get('name', '').lower()
        credible_sources = ['bbc', 'cnn', 'reuters', 'ap news', 'associated press']
        if any(s in source for s in credible_sources):
            score += 1.0
            
        return min(score, 10.0)
    
    def determine_threat_level(self, keyword: str, severity: float) -> str:
        """Determine threat level based on keyword and severity"""
        if severity >= 8.0 or keyword in ['attack', 'conflict', 'explosion']:
            return 'critical'
        elif severity >= 6.0 or keyword in ['earthquake', 'pandemic', 'crisis']:
            return 'high'
        elif severity >= 4.0 or keyword in ['flood', 'wildfire', 'protest']:
            return 'medium'
        else:
            return 'low'