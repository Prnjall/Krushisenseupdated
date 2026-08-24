import os
import sys
import django
sys.path.append(r'p:\Agri Analysis\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

import requests
from datetime import datetime, timedelta, timezone
from predictions.sentinel_hub import get_sentinel_access_token, create_bbox

now = datetime.now(timezone.utc)
start_time = now - timedelta(days=30)
dt_str = f"{start_time.isoformat().replace('+00:00', 'Z')}/{now.isoformat().replace('+00:00', 'Z')}"
print("datetime string:", dt_str)

payload = {
    "collections": ["sentinel-2-l2a"],
    "datetime": dt_str,
    "bbox": create_bbox(18.5204, 73.8567),
    "limit": 10,
    "filter": "eo:cloud_cover <= 20",
    "filter-lang": "cql2-text"
}

token = get_sentinel_access_token()
r = requests.post(
    'https://sh.dataspace.copernicus.eu/catalog/v1/search',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json=payload
)
print(r.status_code)
print(r.text)
