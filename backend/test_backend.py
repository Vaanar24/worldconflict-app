import requests
import json
import time

base_url = "http://localhost:8000"
api_url = f"{base_url}/api/v1"

def test_backend():
    print("\n🔍 Testing Backend Connection...")
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test debug all events
    try:
        response = requests.get(f"{api_url}/events/debug/all")
        data = response.json()
        print(f"\n📊 Collector Stats: {data.get('stats')}")
        print(f"📦 Total events: {data.get('total_events')}")
        if data.get('sample'):
            print(f"\n📝 Sample events ({len(data['sample'])}):")
            for i, event in enumerate(data['sample'][:3]):
                print(f"  {i+1}. {event['type']}: {event['title'][:50]}...")
                print(f"     📍 {event['location']['coordinates']}")
        else:
            print("❌ No events in collector!")
    except Exception as e:
        print(f"❌ Debug endpoint failed: {e}")
    
    # Test stats
    try:
        response = requests.get(f"{api_url}/events/stats?hours=24")
        print(f"\n📊 Stats: {response.json()}")
    except Exception as e:
        print(f"❌ Stats endpoint failed: {e}")
    
    # Test events with world bbox
    try:
        bbox = "-180,-90,180,90"
        response = requests.get(f"{api_url}/events?bbox={bbox}&hours=24")
        data = response.json()
        print(f"\n🗺️ Events in world view: {len(data.get('features', []))}")
    except Exception as e:
        print(f"❌ Events endpoint failed: {e}")

if __name__ == "__main__":
    test_backend()