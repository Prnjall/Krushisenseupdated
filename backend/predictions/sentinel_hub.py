import os
import requests
import time
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

def _load_env():
    if 'SENTINEL_HUB_CLIENT_ID' in os.environ:
        return
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k, v)

_load_env()

_access_token = None
_token_expiry_time = 0

def get_sentinel_access_token() -> str:
    global _access_token, _token_expiry_time
    current_time = time.time()
    if _access_token and current_time < _token_expiry_time - 60:
        return _access_token
        
    client_id = os.environ.get('SENTINEL_HUB_CLIENT_ID')
    client_secret = os.environ.get('SENTINEL_HUB_CLIENT_SECRET')
    if not client_id or not client_secret:
        raise ValueError("Sentinel Hub credentials missing from environment.")
        
    auth_url = 'https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        response = requests.post(auth_url, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        _access_token = data.get('access_token')
        _token_expiry_time = current_time + data.get('expires_in', 3600)
        return _access_token
    except requests.exceptions.RequestException:
        logger.error("Sentinel Hub authentication request failed.")
        raise

def create_bbox(lat, lon, buffer_deg=0.002):
    # buffer_deg of 0.002 is approx 200m at equator
    return [lon - buffer_deg, lat - buffer_deg, lon + buffer_deg, lat + buffer_deg]

def search_latest_observation(lat, lon, days_back=30, max_cloud_cover=20):
    token = get_sentinel_access_token()
    catalog_url = "https://sh.dataspace.copernicus.eu/catalog/v1/search"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(days=days_back)
    
    payload = {
        "collections": ["sentinel-2-l2a"],
        "datetime": f"{start_time.isoformat().replace('+00:00', 'Z')}/{now.isoformat().replace('+00:00', 'Z')}",
        "bbox": create_bbox(lat, lon),
        "limit": 10,
        "filter": f"eo:cloud_cover <= {max_cloud_cover}",
        "filter-lang": "cql2-text"
    }
    
    resp = requests.post(catalog_url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    features = data.get("features", [])
    if not features:
        return None
        
    # Sort descending by datetime
    features.sort(key=lambda x: x["properties"]["datetime"], reverse=True)
    best = features[0]
    
    return {
        "datetime": best["properties"]["datetime"],
        "cloud_cover": best["properties"]["eo:cloud_cover"]
    }

def get_ndvi_statistics(lat, lon, date_str):
    """
    Calls the Statistical API for a given day to get the mean NDVI.
    date_str is ISO format datetime, e.g. '2026-08-20T10:30:00Z'
    """
    token = get_sentinel_access_token()
    stat_url = "https://sh.dataspace.copernicus.eu/statistics/v1"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # We query from start of the previous day to end of the next day to safely bracket the observation
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    start_dt = (dt - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_dt = (dt + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
    from_date = start_dt.isoformat().replace('+00:00', 'Z')
    to_date = end_dt.isoformat().replace('+00:00', 'Z')
    
    evalscript = """
    //VERSION=3
    function setup() {
        return {
            input: ["B04", "B08", "dataMask"],
            output: [
                { id: "ndvi", bands: 1, sampleType: "FLOAT32" },
                { id: "dataMask", bands: 1 }
            ],
            mosaicking: "ORBIT"
        };
    }
    
    function evaluatePixel(samples) {
        let val = 0.0;
        let hasData = 0;
        for (let i = 0; i < samples.length; i++) {
            if (samples[i].dataMask === 1) {
                let denom = samples[i].B08 + samples[i].B04;
                if (denom !== 0) {
                    val = (samples[i].B08 - samples[i].B04) / denom;
                    hasData = 1;
                    break;
                }
            }
        }
        return {
            ndvi: [val],
            dataMask: [hasData]
        };
    }
    """
    
    payload = {
        "input": {
            "bounds": {
                "bbox": create_bbox(lat, lon),
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": from_date,
                        "to": to_date
                    },
                    "maxCloudCoverage": 20
                }
            }]
        },
        "aggregation": {
            "timeRange": {
                "from": from_date,
                "to": to_date
            },
            "aggregationInterval": {
                "of": "P1D"
            },
            "evalscript": evalscript,
            "resx": 0.0001,
            "resy": 0.0001
        }
    }
    
    resp = requests.post(stat_url, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    print("STATS RESPONSE:", data)
    
    # Parse mean NDVI from the response
    intervals = data.get("data", [])
    valid_means = []
    
    for interval in intervals:
        outputs = interval.get("outputs", {})
        if "ndvi" in outputs:
            stats = outputs["ndvi"].get("bands", {}).get("B0", {}).get("stats", {})
            if "mean" in stats:
                val = stats["mean"]
                try:
                    val = float(val)
                    import math
                    if not math.isnan(val):
                        valid_means.append(val)
                except (ValueError, TypeError):
                    pass
                
    if valid_means:
        return sum(valid_means) / len(valid_means)
        
    return None
