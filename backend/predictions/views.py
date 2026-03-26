# Temporary test for model predictions
if __name__ == "__main__":
    import joblib
    from pathlib import Path
    model_path = Path(__file__).resolve().parent / "models" / "crop_recommendation_model.pkl"
    model = joblib.load(model_path)
    test_inputs = [
        [90, 42, 43, 20, 80, 6.5, 200],
        [20, 20, 20, 25, 60, 7, 50]
    ]
    for i, inp in enumerate(test_inputs):
        pred = model.predict([inp])[0]
        print(f"Test input {i+1}: {inp} => Predicted crop: {pred}")
import json
from pathlib import Path
import joblib

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET


# ==============================
# Load ML Models
# ==============================

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

crop_model_path = MODELS_DIR / "crop_recommendation_model.pkl"
yield_model_path = MODELS_DIR / "yield_prediction_model.pkl"


def load_model(path):
    try:
        return joblib.load(path)
    except Exception as e:
        print("Model load error:", e)
        return None


crop_recommendation_model = load_model(crop_model_path)
yield_prediction_model = load_model(yield_model_path)

print("Crop model loaded:", crop_recommendation_model is not None)
print("Yield model loaded:", yield_prediction_model is not None)


# ==============================
# Crop Prediction API
# ==============================

@csrf_exempt
@require_POST
def predict_crop_view(request):
    print("Predict crop API called")
    print("Raw request body:", request.body)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        print("JSON decode error:", e)
        return JsonResponse({
            "success": False,
            "error": f"JSON decode error: {e}"
        }, status=400)

    print(f"Received input: {data}")
    required_fields = ["nitrogen", "phosphorus", "potassium", "temperature", "humidity", "ph", "rainfall"]
    for field in required_fields:
        if field not in data:
            print(f"Missing field: {field}")
            return JsonResponse({
                "success": False,
                "error": f"Missing field: {field}"
            }, status=400)


    try:
        nitrogen = float(data["nitrogen"])
        phosphorus = float(data["phosphorus"])
        potassium = float(data["potassium"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        ph = float(data["ph"])
        rainfall = float(data["rainfall"])
        # Check for NaN or None
        values = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
        if any((v is None or v != v) for v in values):
            raise ValueError("All inputs must be valid numbers (not blank or NaN)")
    except Exception as e:
        print("Input conversion error:", e)
        return JsonResponse({
            "success": False,
            "error": f"Input conversion error: {e}"
        }, status=400)

    print(f"Parsed values: N={nitrogen}, P={phosphorus}, K={potassium}, Temp={temperature}, Humidity={humidity}, pH={ph}, Rainfall={rainfall}")

    model_input = [[
        nitrogen,
        phosphorus,
        potassium,
        temperature,
        humidity,
        ph,
        rainfall
    ]]
    print("Model input:", model_input)

    if crop_recommendation_model is None:
        print("Prediction error: Crop recommendation model not loaded")
        return JsonResponse({
            "success": False,
            "error": "Crop recommendation model not loaded"
        }, status=500)

    # Get probability scores for all crops
    proba = crop_recommendation_model.predict_proba(model_input)[0]
    class_labels = crop_recommendation_model.classes_
    # Pair labels with probabilities
    label_proba = list(zip(class_labels, proba))
    # Debug: print all crop probabilities (unsorted)
    print("All crop probabilities:")
    for label, prob in label_proba:
        print(f"  {label}: {prob:.4f}")

    # Sort by probability descending
    label_proba_sorted = sorted(label_proba, key=lambda x: x[1], reverse=True)
    print("Sorted crop probabilities:")
    for label, prob in label_proba_sorted:
        print(f"  {label}: {prob:.4f}")

    # --- Hybrid Recommendation Logic ---
    import pandas as pd
    import numpy as np
    dataset_path = Path(__file__).resolve().parent.parent / "ml" / "data" / "Crop_recommendation.csv"
    df = pd.read_csv(dataset_path)
    feature_cols = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    input_vec = np.array([nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall])

    # 1. Model prediction for primary crop
    primary_crop = crop_recommendation_model.predict([input_vec])[0]
    print(f"Model predicted crop: {primary_crop}")

    # Related crops mapping
    relatedCrops = {
        "rice": ["coconut", "papaya"],
        "maize": ["cotton", "sugarcane"],
        "chickpea": ["lentil", "pigeonpeas"],
        "kidneybeans": ["blackgram", "mothbeans"],
        "pigeonpeas": ["mungbean", "lentil"],
        "mothbeans": ["mungbean", "blackgram"],
        "mungbean": ["mothbeans", "lentil"],
        "blackgram": ["mothbeans", "mungbean"],
        "lentil": ["chickpea", "pigeonpeas"],
        "pomegranate": ["grapes", "apple"],
        "banana": ["papaya", "coconut"],
        "mango": ["papaya", "orange"],
        "grapes": ["apple", "pomegranate"],
        "watermelon": ["muskmelon", "cucumber"],
        "muskmelon": ["watermelon", "cucumber"],
        "apple": ["grapes", "pomegranate"],
        "orange": ["mango", "papaya"],
        "papaya": ["banana", "coconut"],
        "coconut": ["banana", "papaya"],
        "cotton": ["maize", "jute"],
        "jute": ["cotton", "rice"],
        "coffee": ["coconut", "banana"]
    }

    # 2. Fetch related crops from mapping
    related = relatedCrops.get(str(primary_crop).lower(), [])
    # 3. Compose result: primary + up to 2 related crops, no duplicates
    final_crops = [primary_crop]
    for crop in related:
        if crop != primary_crop and crop not in final_crops:
            final_crops.append(crop)
        if len(final_crops) == 3:
            break
    print("Selected crops (final recommendations):", final_crops)

    return JsonResponse({
        "success": True,
        "recommendations": final_crops
    })
# ==============================
# Health Check API
# ==============================

@require_GET
def health_check_view(request):
    models_loaded = (
        crop_recommendation_model is not None and
        yield_prediction_model is not None
    )
    return JsonResponse({
        "success": True,
        "models_loaded": models_loaded
    })
