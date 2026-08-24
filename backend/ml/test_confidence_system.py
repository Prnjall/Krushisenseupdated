import urllib.request
import json

url = "http://127.0.0.1:8000/api/predict-crop"

headers = {
    "Content-Type": "application/json"
}

tests = [
    {
        "name": "1. Known dataset-like input (Rice-like)",
        "data": {
            "nitrogen": 90,
            "phosphorus": 42,
            "potassium": 43,
            "temperature": 20,
            "humidity": 80,
            "ph": 6.5,
            "rainfall": 200
        }
    },
    {
        "name": "2. Slightly modified known input",
        "data": {
            "nitrogen": 95,
            "phosphorus": 45,
            "potassium": 45,
            "temperature": 22,
            "humidity": 82,
            "ph": 6.8,
            "rainfall": 210
        }
    },
    {
        "name": "3. Moderately different input",
        "data": {
            "nitrogen": 110,
            "phosphorus": 60,
            "potassium": 55,
            "temperature": 28,
            "humidity": 65,
            "ph": 6.2,
            "rainfall": 120
        }
    },
    {
        "name": "4. Far-away input",
        "data": {
            "nitrogen": 150,
            "phosphorus": 140,
            "potassium": 200,
            "temperature": 45,
            "humidity": 20,
            "ph": 8.0,
            "rainfall": 50
        }
    }
]

print("--- TESTING CONFIDENCE SYSTEM API ---")
for t in tests:
    print(f"\n{t['name']}")
    print(f"Input: {t['data']}")
    
    try:
        req = urllib.request.Request(url, data=json.dumps(t['data']).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                res = json.loads(response.read().decode('utf-8'))
                print(f"Predicted crop: {res.get('prediction')}")
                top3 = [f"{c['crop']} ({c['probability']:.2f})" for c in res.get('top3', [])]
                print(f"Top 3 crops: {', '.join(top3)}")
                print(f"Top probability: {res.get('confidence')}")
                print(f"Nearest training distance: {res.get('nearest_sample_distance')}")
                print(f"Mean 5-nearest distance: {res.get('mean_5_nearest_distance')}")
                print(f"Prediction status: {res.get('prediction_status')}")
                print(f"Warning: {res.get('warning', 'None')}")
            else:
                print(f"Error {response.status}: {response.read()}")
    except Exception as e:
        print(f"Request failed: {e}")

print("\nDONE")
