import os
import sys
import django
sys.path.append(r'p:\Agri Analysis\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import requests
from datetime import datetime, timedelta
from predictions.sentinel_hub import search_latest_observation, get_sentinel_access_token, create_bbox

def check_location(name, lat, lon):
    print(f"=== TESTING {name} ({lat}, {lon}) ===")
    
    # 1. Search Catalog
    try:
        obs = search_latest_observation(lat, lon, days_back=180, max_cloud_cover=20)
        if not obs:
            print("NO_RECENT_DATA")
            return
    except Exception as e:
        print("Catalog Error:", e)
        return
        
    print(f"Observation Date: {obs['datetime']}")
    print(f"Cloud Cover: {obs['cloud_cover']}%")
    
    from predictions.sentinel_hub import get_ndvi_statistics
    ndvi_val = get_ndvi_statistics(lat, lon, obs['datetime'])
    print("Calculated NDVI:", ndvi_val)
        
    print()

# Test 1: Nashik, Maharashtra (Grape farming region)
check_location("Nashik Farm", 20.0110, 73.7903)

# Test 2: Guntur, Andhra Pradesh (Chilli farming region)
check_location("Guntur Farm", 16.3067, 80.4365)

# Test 3: Dubai (desert)
check_location("Dubai", 25.276987, 55.296249)
