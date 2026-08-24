import urllib.request, json
data = json.dumps({
    "language": "en",
    "location": {"region": "Nashik, Maharashtra"},
    "soil": {"N": 90, "P": 42, "K": 43, "pH": 6.5},
    "environment": {"temperature": 25.5, "humidity": 65, "rainfall_annual": 200},
    "weather_current": {"temperature": 26, "precipitation": 0},
    "satellite": {"status": "AVAILABLE", "ndvi": 0.294, "days_since": 2, "cloud_cover": 18.38},
    "prediction": {
        "primary_crop": "rice",
        "top3": [{"crop": "rice", "prob": 0.85}],
        "familiarity": "high",
        "prediction_status": "high_confidence"
    }
}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/api/agri-advisory', data=data, headers={'Content-Type': 'application/json'})
try:
    print(urllib.request.urlopen(req).read().decode('utf-8'))
except Exception as e:
    print(e)
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
