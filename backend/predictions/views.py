import json
import io
from PIL import Image
import onnxruntime as ort
import logging
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

logger = logging.getLogger(__name__)


# ==============================
# Load ML Models
# ==============================

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

crop_model_path = MODELS_DIR / "crop_recommendation_model.pkl"
yield_model_path = MODELS_DIR / "yield_prediction_model.pkl"
scaler_path = MODELS_DIR / "scaler.pkl"
x_train_path = MODELS_DIR / "X_train_scaled.npy"

# Familiarity Thresholds (calibrated on validation set)
# Based on Mean 5-Nearest Distances
FAMILIARITY_HIGH = 0.62       # ~90th percentile
FAMILIARITY_MODERATE = 0.86   # ~99th percentile
FAMILIARITY_LOW = 1.35        # ~Max validation distance


def load_model(path):
    try:
        return joblib.load(path)
    except Exception as e:
        print("Model load error:", e)
        return None


crop_recommendation_model = load_model(crop_model_path)
yield_prediction_model = load_model(yield_model_path)
scaler = load_model(scaler_path)

nn_model = None
if scaler is not None and x_train_path.exists():
    try:
        X_train_scaled = np.load(x_train_path)
        nn_model = NearestNeighbors(n_neighbors=5)
        nn_model.fit(X_train_scaled)
        print("NearestNeighbors model fitted successfully.")
    except Exception as e:
        print("Error fitting NearestNeighbors model:", e)

print("Crop model loaded:", crop_recommendation_model is not None)
print("Yield model loaded:", yield_prediction_model is not None)
print("Scaler loaded:", scaler is not None)


# ==============================
# Crop Prediction API
# ==============================

@csrf_exempt
@require_POST
def predict_crop_view(request):
    logger.debug("Predict crop API called")
    logger.info(f"Predict crop request: {request.content_type}, length: {len(request.body)}")

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        logger.error(f"JSON decode error: {e}")
        return JsonResponse({
            "success": False,
            "error": "Invalid request data"
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
        import math
        nitrogen = float(data["nitrogen"])
        phosphorus = float(data["phosphorus"])
        potassium = float(data["potassium"])
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        ph = float(data["ph"])
        rainfall = float(data["rainfall"])
        
        # Check for NaN or None
        values = [nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall]
        if any((v is None or math.isnan(v)) for v in values):
            raise ValueError("All inputs must be valid numbers (not blank or NaN)")
        
        # Check for finite values
        if any(math.isinf(v) for v in values):
            raise ValueError("All inputs must be finite numbers")
            
        # Validation bounds
        if not (-50 <= temperature <= 60):
            return JsonResponse({
                "success": False,
                "error": f"Validation error: temperature {temperature} is outside reasonable bounds (-50 to 60 °C)."
            }, status=400)
            
        if not (0 <= humidity <= 100):
            return JsonResponse({
                "success": False,
                "error": f"Validation error: humidity {humidity} is outside reasonable bounds (0 to 100 %)."
            }, status=400)
            
        if not (0 <= rainfall <= 10000):
            return JsonResponse({
                "success": False,
                "error": f"Validation error: rainfall {rainfall} is outside reasonable bounds (0 to 10000 mm)."
            }, status=400)
            
    except Exception as e:
        logger.error(f"Input conversion error: {e}")
        return JsonResponse({
            "success": False,
            "error": "Invalid input data"
        }, status=400)

    print(f"Parsed values: N={nitrogen}, P={phosphorus}, K={potassium}, Temp={temperature}, Humidity={humidity}, pH={ph}, Rainfall={rainfall}")

    # The Random Forest must receive a pandas DataFrame with these exact column names
    model_input_df = pd.DataFrame([[
        nitrogen,
        phosphorus,
        potassium,
        temperature,
        humidity,
        ph,
        rainfall
    ]], columns=["N", "P", "K", "temperature", "humidity", "ph", "rainfall"])
    
    print("Model input DataFrame:\n", model_input_df)

    if crop_recommendation_model is None:
        print("Prediction error: Crop recommendation model not loaded")
        return JsonResponse({
            "success": False,
            "error": "Crop recommendation model not loaded"
        }, status=500)

    # Get probability scores for all crops
    proba = crop_recommendation_model.predict_proba(model_input_df)[0]
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
    # 1. Model prediction for primary crop
    primary_crop = crop_recommendation_model.predict(model_input_df)[0]
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

    # --- Confidence / Familiarity Check ---
    prediction_status = "low_confidence"
    warning = None
    nearest_dist = -1.0
    mean_5_dist = -1.0
    data_familiarity = "low"
    top1_prob = label_proba_sorted[0][1]

    if scaler is not None and nn_model is not None:
        try:
            # Scale input using training scaler
            scaled_input = scaler.transform(model_input_df)
            # Find distances
            distances, _ = nn_model.kneighbors(scaled_input)
            nearest_dist = float(distances[0][0])
            mean_5_dist = float(np.mean(distances[0]))
            
            # Determine status based on mean 5-nearest distance
            if mean_5_dist <= FAMILIARITY_HIGH:
                data_familiarity = "high"
                if top1_prob >= 0.5:
                    prediction_status = "high_confidence"
                else:
                    prediction_status = "moderate_confidence"
                    warning = "The model is somewhat uncertain between multiple crops."
            elif mean_5_dist <= FAMILIARITY_MODERATE:
                data_familiarity = "moderate"
                prediction_status = "moderate_confidence"
                warning = "The supplied conditions are somewhat different from the training data."
            elif mean_5_dist <= FAMILIARITY_LOW:
                data_familiarity = "low"
                prediction_status = "low_confidence"
                warning = "The supplied conditions are quite different from known training samples. The model has limited training data for these conditions."
            else:
                data_familiarity = "insufficient"
                prediction_status = "insufficient_data"
                warning = "The supplied conditions are outside the range well represented by our training data. The recommendation should be treated as an estimate, not a reliable crop recommendation."
        except Exception as e:
            print("Error calculating familiarity:", e)

    response_data = {
        "success": True,
        "recommendations": final_crops,
        "prediction": primary_crop,
        "top3": [{"crop": c, "probability": p} for c, p in label_proba_sorted[:3]],
        "confidence": float(top1_prob),
        "prediction_status": prediction_status,
        "nearest_sample_distance": nearest_dist,
        "mean_5_nearest_distance": mean_5_dist,
        "data_familiarity": data_familiarity
    }
    
    if warning:
        response_data["warning"] = warning

    return JsonResponse(response_data)
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

# ==============================
# Weather API
# ==============================

import urllib.request
from django.core.cache import cache

def build_weather_risk_signals(forecast):
    signals = []
    rainy_days = sum(1 for day in forecast if day.get("precipitation_sum", 0) > 0.1)
    if rainy_days >= 4:
        signals.append("Rain is forecast on multiple upcoming days.")
    elif rainy_days <= 1:
        signals.append("Little or no precipitation is forecast across most of the outlook.")
        
    temps = [day.get("temperature_max") for day in forecast if day.get("temperature_max") is not None]
    if temps:
        if max(temps) - min(temps) >= 8:
            signals.append("The warmest forecast day is considerably warmer than the coolest.")
            
    high_rain_prob = sum(1 for day in forecast if day.get("precipitation_probability", 0) >= 60)
    if high_rain_prob >= 2:
        signals.append("High rain probability occurs on upcoming days.")
        
    consecutive_dry = 0
    max_dry = 0
    for day in forecast:
        if day.get("precipitation_sum", 0) <= 0.1:
            consecutive_dry += 1
            max_dry = max(max_dry, consecutive_dry)
        else:
            consecutive_dry = 0
    if max_dry >= 4:
        signals.append("Several consecutive days have no forecast precipitation.")
        
    return list(set(signals))
import urllib.request

@require_GET
def get_weather_view(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    
    if not lat or not lon:
        return JsonResponse({"success": False, "error": "Missing lat or lon parameters"}, status=400)
        
    try:
        lat_f = float(lat)
        lon_f = float(lon)
        cache_key = f"weather_{round(lat_f, 3)}_{round(lon_f, 3)}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return JsonResponse(cached_data)
            
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat_f}&longitude={lon_f}&current=temperature_2m,relative_humidity_2m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code&timezone=auto&forecast_days=7"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        if "error" in data:
            return JsonResponse({"success": False, "error": data.get("reason", "Unknown Open-Meteo error")}, status=400)
            
        weather_obj = {
            "temperature": data["current"]["temperature_2m"],
            "humidity": data["current"]["relative_humidity_2m"],
            "current_precipitation": data["current"]["precipitation"]
        }
        
        forecast = []
        if "daily" in data:
            daily = data["daily"]
            time_arr = daily.get("time", [])
            for i in range(len(time_arr)):
                forecast.append({
                    "date": time_arr[i],
                    "temperature_max": daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
                    "temperature_min": daily.get("temperature_2m_min", [])[i] if i < len(daily.get("temperature_2m_min", [])) else None,
                    "precipitation_sum": daily.get("precipitation_sum", [])[i] if i < len(daily.get("precipitation_sum", [])) else None,
                    "precipitation_probability": daily.get("precipitation_probability_max", [])[i] if i < len(daily.get("precipitation_probability_max", [])) else None,
                    "weather_code": daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else None
                })
                
        forecast_summary = {}
        if forecast:
            temps_max = [day["temperature_max"] for day in forecast if day.get("temperature_max") is not None]
            temps_min = [day["temperature_min"] for day in forecast if day.get("temperature_min") is not None]
            precip = [day["precipitation_sum"] for day in forecast if day.get("precipitation_sum") is not None]
            precip_prob = [day["precipitation_probability"] for day in forecast if day.get("precipitation_probability") is not None]
            
            forecast_summary = {
                "days_available": len(forecast),
                "highest_temperature": max(temps_max) if temps_max else None,
                "lowest_temperature": min(temps_min) if temps_min else None,
                "total_precipitation": sum(precip) if precip else 0,
                "rainiest_day": max(forecast, key=lambda d: d.get("precipitation_sum") or 0).get("date") if precip else None,
                "max_precipitation_probability": max(precip_prob) if precip_prob else 0
            }
            
        risk_signals = build_weather_risk_signals(forecast)
        
        response_data = {
            "success": True,
            "weather": weather_obj,
            "forecast": forecast,
            "forecast_summary": forecast_summary,
            "risk_signals": risk_signals
        }
        
        # Cache for 3 hours
        cache.set(cache_key, response_data, 60 * 60 * 3)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        return JsonResponse({"success": False, "error": "Weather data is currently unavailable. Please try again later."}, status=500)

from .sentinel_hub import search_latest_observation, get_ndvi_statistics
from datetime import datetime, timezone

# ==============================
# Satellite Test API
# ==============================
from .sentinel_hub import get_sentinel_access_token

@require_GET
def satellite_test_view(request):
    try:
        token = get_sentinel_access_token()
        if token:
            return JsonResponse({
                "success": True,
                "provider": "Sentinel Hub",
                "authenticated": True,
                "message": "Sentinel Hub authentication successful"
            })
    except Exception as e:
        logger.error(f"Satellite Auth Error: {str(e)}")
        return JsonResponse({
            "success": False,
            "provider": "Sentinel Hub",
            "authenticated": False,
            "error": "Sentinel Hub authentication failed"
        }, status=500)

# ==============================
# Satellite NDVI API
# ==============================

@require_GET
def satellite_ndvi_view(request):
    lat_str = request.GET.get('lat')
    lon_str = request.GET.get('lon')
    
    if not lat_str or not lon_str:
        return JsonResponse({"success": False, "error": "Missing lat or lon parameters"}, status=400)
        
    try:
        lat = float(lat_str)
        lon = float(lon_str)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return JsonResponse({"success": False, "error": "Invalid coordinates"}, status=400)
    except ValueError:
        return JsonResponse({"success": False, "error": "Coordinates must be numbers"}, status=400)

    # Cache key based on rounded coordinates (approx 1.1km grid)
    cache_key = f"ndvi_{round(lat, 3)}_{round(lon, 3)}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        # Avoid caching fake results/errors - only successful ones are cached
        return JsonResponse(cached_data)

    try:
        obs = search_latest_observation(lat, lon, days_back=30, max_cloud_cover=20)
        if not obs:
            return JsonResponse({
                "success": False,
                "status": "NO_RECENT_DATA",
                "message": "Satellite data unavailable for this period, possibly due to cloud cover."
            })
            
        date_str = obs["datetime"]
        cloud_cover = obs["cloud_cover"]
        
        ndvi_val = get_ndvi_statistics(lat, lon, date_str)
        
        if ndvi_val is None or not (-1 <= ndvi_val <= 1):
            return JsonResponse({
                "success": False,
                "status": "INVALID_DATA",
                "message": "Could not calculate a valid NDVI for this area."
            })
            
        # Calculate days since observation
        obs_dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        days_since = (datetime.now(timezone.utc) - obs_dt).days
        
        response_data = {
            "success": True,
            "indicator": "NDVI",
            "value": ndvi_val,
            "date_acquired": date_str,
            "cloud_cover_percentage": cloud_cover,
            "source": "Sentinel-2 L2A",
            "days_since_observation": days_since
        }
        
        # Cache successful response for 6 hours
        cache.set(cache_key, response_data, 60 * 60 * 6)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Satellite API Error: {str(e)}")
        return JsonResponse({
            "success": False,
            "status": "SERVER_ERROR",
            "message": "Satellite data unavailable for this period, possibly due to network errors."
        }, status=500)

# ==============================
# AI Agricultural Advisory API
# ==============================

import os
from google import genai
from google.genai import types

@csrf_exempt
@require_POST
def agri_advisory_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    # 1. Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return JsonResponse({
            "success": False,
            "status": "AI_NOT_CONFIGURED",
            "message": "AI advisory is currently unavailable."
        })

    # 2. Validate Inputs
    try:
        language = data.get("language", "en")
        if language not in ["en", "hi", "mr"]:
            return JsonResponse({"success": False, "error": "Unsupported language"}, status=400)

        # Map language code to full name for unambiguous Gemini instruction
        language_names = {"en": "English", "hi": "Hindi (हिन्दी)", "mr": "Marathi (मराठी)"}
        language_full = language_names.get(language, "English")

        location = data.get("location", {})
        soil = data.get("soil", {})
        env = data.get("environment", {})
        weather = data.get("weather_current", {})
        weather_forecast = data.get("weather_forecast", {})
        satellite = data.get("satellite", {})
        prediction = data.get("prediction", {})

        # Basic type checks to prevent malformed data going to Gemini
        if not isinstance(soil.get("N"), (int, float)):
            return JsonResponse({"success": False, "error": "Malformed numeric data"}, status=400)
            
        weather_temperature = weather.get("temperature")
        weather_precipitation = weather.get("precipitation")
        
        if weather_temperature is not None and not isinstance(weather_temperature, (int, float)):
            return JsonResponse({"success": False, "error": "Malformed numeric data"}, status=400)
            
        if weather_precipitation is not None and not isinstance(weather_precipitation, (int, float)):
            return JsonResponse({"success": False, "error": "Malformed numeric data"}, status=400)
            
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Validation error: {e}"}, status=400)

    # 3. Build Prompt Data
    
    if not weather:
        weather_status = "UNAVAILABLE"
        weather_str = "Status: UNAVAILABLE"
    else:
        weather_status = "AVAILABLE"
        weather_str = f"Temperature: {weather.get('temperature')} C\nPrecipitation: {weather.get('precipitation')} mm"
        
    forecast_str = ""
    if weather_forecast.get("status") == "AVAILABLE":
        summary = weather_forecast.get("summary", {})
        signals = weather_forecast.get("risk_signals", [])
        forecast_str += f"""
FORECAST SUMMARY (Next {summary.get('days_available', 7)} days):
Highest Temp: {summary.get('highest_temperature')} C
Lowest Temp: {summary.get('lowest_temperature')} C
Total Precipitation: {summary.get('total_precipitation')} mm
Rainiest Day: {summary.get('rainiest_day')}
Max Rain Probability: {summary.get('max_precipitation_probability')}%

AGRICULTURAL WEATHER RISK SIGNALS:
{chr(10).join(f"- {s}" for s in signals) if signals else "None detected."}
"""
    else:
        forecast_str += "FORECAST: UNAVAILABLE\n"

    # Prepare text representation for Gemini
    prompt_text = f"""
OUTPUT LANGUAGE: {language_full} — ALL advisory string values must be in {language_full}.
Language code: {language}
Location: {location.get("region", "Unknown")}

SOIL DATA:
Nitrogen (N): {soil.get("N")}
Phosphorus (P): {soil.get("P")}
Potassium (K): {soil.get("K")}
pH: {soil.get("pH")}

ENVIRONMENTAL CONTEXT (Historical/Annual used for ML):
Temperature: {env.get("temperature")} C
Humidity: {env.get("humidity")}%
Annual Rainfall: {env.get("rainfall_annual")} mm

CURRENT WEATHER:
{weather_str}

SATELLITE DATA:
Status: {satellite.get("status", "UNAVAILABLE")}
"""
    if satellite.get("status") == "AVAILABLE":
        prompt_text += f"NDVI: {satellite.get('ndvi')}\nDays since observation: {satellite.get('days_since')}\nCloud Cover: {satellite.get('cloud_cover')}%\n"

    prompt_text += f"""
CROP PREDICTION (Machine Learning Output):
Primary Recommendation: {prediction.get("primary_crop")}
Top 3 Recommendations: {json.dumps(prediction.get("top3"))}
Familiarity/Confidence Status: {prediction.get("prediction_status")}
"""
    
    if prediction.get("prediction_status") in ["low_confidence", "insufficient_data"]:
        prompt_text += "\nCRITICAL: The model has insufficient familiarity with these conditions. You MUST add a strong disclaimer in the 'summary' and 'cautions' sections advising the farmer to consult local experts, and state that this is merely a broad estimate."

    if satellite.get("status") != "AVAILABLE":
        prompt_text += "\nCRITICAL: If satellite data is unavailable, state that satellite data is unavailable in the satellite_insight. Never estimate or invent an NDVI value."

    if weather_status != "AVAILABLE":
        prompt_text += "\nCRITICAL: Current weather data is unavailable. Do not invent temperature, humidity, precipitation, rainfall, or weather conditions. Avoid weather-specific advice that depends on missing values."
        
    if weather_forecast.get("status") != "AVAILABLE":
        prompt_text += "\nCRITICAL: The upcoming weather forecast is unavailable. Do not invent future temperature, rainfall, precipitation probability, storms, dry spells, or future weather conditions."
    else:
        prompt_text += f"{forecast_str}"

    # Final mandatory language override — appended LAST so Gemini sees it immediately before generating
    prompt_text += f"""

=== FINAL MANDATORY OUTPUT LANGUAGE REMINDER ===
You MUST write ALL advisory text values in {language_full}.
Do NOT write any advisory sentence or bullet point in English if the requested language is not English.
The JSON keys remain in English. Only the string VALUES must be in {language_full}.
If you are generating in Hindi or Marathi, use natural colloquial farmer-friendly language, not a word-for-word literal translation.
Do not invent or alter any numbers, units, or measurements.
=== END ==="""

    system_instruction = f"""=== MANDATORY OUTPUT LANGUAGE: {language_full} ===
EVERY human-readable string value in the JSON response MUST be written in {language_full}.
This is a non-negotiable hard requirement. Do NOT generate any advisory text in English if the language is not English.
The JSON keys (summary, crop_explanation, weather_advice, etc.) must remain in English for API compatibility.
Only the string VALUES must be in {language_full}.
The field descriptions in the schema are structural guides only — they do NOT define the output language.
=== END OF LANGUAGE REQUIREMENT ===

You are an agricultural advisory assistant for KrushiSense.
Your job is to provide practical, localized, cautious and evidence-grounded agricultural guidance.
You are NOT the crop prediction model. The supplied ML recommendation is an input signal that you must explain, not blindly override.
Use ONLY the structured information supplied in the request and general agricultural knowledge appropriate for the identified crop and region.
Never invent missing measurements, weather conditions, NDVI, crop probabilities, or satellite observations.
Never claim that NDVI alone proves crop health or that a recommendation guarantees yield.
Clearly distinguish observed data from general agricultural guidance.
When data is unavailable, explicitly say it is unavailable in {language_full}.
Give practical recommendations in simple farmer-friendly language appropriate for {language_full}-speaking farmers.
Prefer sustainable and regenerative agricultural practices (crop rotation, residue/mulch management, soil organic matter, water conservation, integrated nutrient/pest management, cover crops) where appropriate for the given crop and soil conditions.
Do not provide dangerous or unsupported pesticide dosage instructions.
If confidence/familiarity is low or insufficient, clearly communicate that limitation in {language_full}.

NUMERIC DATA PRESERVATION RULES (apply regardless of language):
- Preserve all numerical values exactly as provided: N, P, K, pH, temperature, humidity, rainfall, precipitation, NDVI, confidence percentages, dates, units.
- Do not alter, invent, round, or omit any numeric measurement.
- Units (C, mm, %, kg/ha) must be preserved as-is.

Return ONLY the required structured JSON response with all string values in {language_full}."""

    try:
        client = genai.Client(api_key=api_key)
        
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "summary": {"type": "STRING", "description": "Brief 2-sentence agricultural summary."},
                "crop_explanation": {"type": "STRING", "description": "Why this crop suits the current soil and weather."},
                "weather_advice": {"type": "STRING", "description": "Immediate actions based on current weather/precipitation."},
                "soil_advice": {"type": "STRING", "description": "Fertilizer/amendment suggestions based on N-P-K-pH."},
                "satellite_insight": {"type": "STRING", "description": "Interpretation of the NDVI value, or state unavailable."},
                "sustainable_practices": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                },
                "next_steps": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                },
                "cautions": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                }
            },
            "required": ["summary", "crop_explanation", "weather_advice", "soil_advice", "satellite_insight", "sustainable_practices", "next_steps", "cautions"]
        }

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.2,
            ),
        )
        
        advisory_data = json.loads(response.text)
        
        return JsonResponse({
            "success": True,
            "advisory": advisory_data
        })

    except Exception as e:
        logger.error(f"Gemini API Error: {str(e)}")
        return JsonResponse({
            "success": False,
            "status": "AI_UNAVAILABLE",
            "message": "AI advisory is temporarily unavailable."
        })


# Temporary test for model predictions

# ==============================
# Load Disease Model
# ==============================
DISEASE_MODELS_DIR = MODELS_DIR / "disease_model"
disease_onnx_path = DISEASE_MODELS_DIR / "disease_classifier.onnx"
class_names_path = DISEASE_MODELS_DIR / "class_names.json"
preprocessing_path = DISEASE_MODELS_DIR / "preprocessing.json"
metadata_path = DISEASE_MODELS_DIR / "model_metadata.json"

disease_session = None
disease_class_names = []
disease_preprocessing = {}
disease_confidence_threshold = 0.60

try:
    if disease_onnx_path.exists():
        disease_session = ort.InferenceSession(str(disease_onnx_path), providers=['CPUExecutionProvider'])
        
    if class_names_path.exists():
        with open(class_names_path, "r") as f:
            disease_class_names = json.load(f)
            
    if preprocessing_path.exists():
        with open(preprocessing_path, "r") as f:
            disease_preprocessing = json.load(f)
            
    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            md = json.load(f)
            disease_confidence_threshold = md.get("confidence_threshold", 0.60)
            
    logger.info("Disease model artifacts loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load disease model artifacts: {e}")

DISEASE_CROP_MAPPING = {
    'apple': ['apple_healthy', 'apple_scab', 'apple_black_rot'],
    'maize': ['maize_healthy', 'maize_cercospora_leaf_spot', 'maize_common_rust', 'maize_northern_leaf_blight'],
    'grapes': ['grape_healthy', 'grape_black_rot', 'grape_esca', 'grape_leaf_blight'],
    'rice': ['rice_healthy', 'rice_bacterial_leaf_blight', 'rice_brown_spot', 'rice_leaf_smut']
}

def format_disease_name(class_name):
    if class_name.endswith("_healthy"):
        return "Healthy"
    # e.g., apple_black_rot -> Apple Black Rot
    parts = class_name.split("_")
    return " ".join([p.capitalize() for p in parts])

# ==============================
# Disease Detection API
# ==============================
@csrf_exempt
@require_POST
def disease_detection_view(request):
    try:
        # 1. Model Availability Check
        if not disease_session or not disease_class_names or not disease_preprocessing:
            return JsonResponse({
                "success": False,
                "status": "ANALYSIS_UNAVAILABLE",
                "message": "Disease detection model is currently unavailable."
            })
            
        # 2. Crop Validation
        crop = request.POST.get("crop", "").lower().strip()
        if crop not in DISEASE_CROP_MAPPING:
            return JsonResponse({
                "success": False,
                "status": "UNSUPPORTED_CROP",
                "message": "Disease detection is currently unavailable for this crop."
            })
            
        # 3. Image Validation
        if "image" not in request.FILES:
            return JsonResponse({
                "success": False,
                "status": "INVALID_IMAGE",
                "message": "No image provided."
            })
            
        image_file = request.FILES["image"]
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                "success": False,
                "status": "INVALID_IMAGE",
                "message": "Image size exceeds 5MB."
            })
            
        try:
            image_data = image_file.read()
            img = Image.open(io.BytesIO(image_data))
            img.verify() # Verify it's an actual image
            
            # Re-open for processing because verify() breaks the file pointer
            img = Image.open(io.BytesIO(image_data)).convert('RGB')
        except Exception:
            return JsonResponse({
                "success": False,
                "status": "INVALID_IMAGE",
                "message": "Invalid or corrupted image format."
            })
            
        # 4. Preprocessing
        # Uses ImageNet stats by default as per preprocessing.json
        img = img.resize((224, 224), Image.BILINEAR)
        img_np = np.array(img).astype(np.float32) / 255.0
        
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img_np = (img_np - mean) / std
        
        # HWC to CHW
        img_np = np.transpose(img_np, (2, 0, 1))
        # Add batch dimension
        img_np = np.expand_dims(img_np, axis=0).astype(np.float32)
        
        # 5. Inference
        input_name = disease_session.get_inputs()[0].name
        logits = disease_session.run(None, {input_name: img_np})[0]
        
        # Softmax
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        probs = probs[0]
        
        pred_idx = int(np.argmax(probs))
        pred_class = disease_class_names[str(pred_idx)]
        confidence = float(probs[pred_idx])
        
        # 6. Post-Processing & Safety Validation
        allowed_classes = DISEASE_CROP_MAPPING[crop]
        
        if pred_class not in allowed_classes or confidence < disease_confidence_threshold:
            return JsonResponse({
                "success": True,
                "status": "LOW_CONFIDENCE",
                "crop": crop,
                "diagnosis": None,
                "confidence": round(confidence, 4)
            })
            
        if pred_class.endswith("_healthy"):
            status = "HEALTHY"
        else:
            status = "DISEASE_DETECTED"
            
        return JsonResponse({
            "success": True,
            "status": status,
            "crop": crop,
            "diagnosis": {
                "disease": format_disease_name(pred_class),
                "class_name": pred_class,
                "confidence": round(confidence, 4)
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Disease detection error: {e}")
        # Never expose internal Python stack traces
        return JsonResponse({
            "success": False,
            "status": "ANALYSIS_UNAVAILABLE",
            "message": "An error occurred during analysis."
        })

# ==============================
# AI Disease Advisory API
# ==============================

@csrf_exempt
@require_POST
def disease_advisory_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    # 1. Check API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return JsonResponse({
            "success": False,
            "status": "AI_NOT_CONFIGURED",
            "message": "AI advisory is currently unavailable."
        })

    # 2. Validate Inputs
    try:
        language = data.get("language", "en")
        if language not in ["en", "hi", "mr"]:
            return JsonResponse({"success": False, "error": "Unsupported language"}, status=400)

        # Map language code to full name for unambiguous Gemini instruction
        language_names = {"en": "English", "hi": "Hindi (हिन्दी)", "mr": "Marathi (मराठी)"}
        language_full = language_names.get(language, "English")

        crop = data.get("crop")
        if not crop:
            return JsonResponse({"success": False, "error": "Missing crop"}, status=400)

        diagnosis = data.get("diagnosis", {})
        status = diagnosis.get("status")
        
        # Only allow Gemini to process valid HEALTHY or DISEASE_DETECTED results
        if status not in ["HEALTHY", "DISEASE_DETECTED"]:
            return JsonResponse({
                "success": True,
                "status": status if status else "LOW_CONFIDENCE",
                "advisory": None,
                "message": "A reliable disease advisory cannot be generated because the screening result is uncertain or invalid."
            })

        location = data.get("location", {})
        weather = data.get("weather_current", {})
        weather_forecast = data.get("weather_forecast", {})
        satellite = data.get("satellite", {})
        
        # Basic type checks for weather to prevent malformed data
        weather_temperature = weather.get("temperature")
        weather_precipitation = weather.get("precipitation")
        
        if weather_temperature is not None and not isinstance(weather_temperature, (int, float)):
            return JsonResponse({"success": False, "error": "Malformed numeric data"}, status=400)
            
        if weather_precipitation is not None and not isinstance(weather_precipitation, (int, float)):
            return JsonResponse({"success": False, "error": "Malformed numeric data"}, status=400)
            
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Validation error: {e}"}, status=400)

    # 3. Build Prompt Data
    
    if not weather:
        weather_status = "UNAVAILABLE"
        weather_str = "Status: UNAVAILABLE"
    else:
        weather_status = "AVAILABLE"
        weather_str = f"Temperature: {weather.get('temperature')} C\nPrecipitation: {weather.get('precipitation')} mm"
        
    forecast_str = ""
    if weather_forecast.get("status") == "AVAILABLE":
        summary = weather_forecast.get("summary", {})
        signals = weather_forecast.get("risk_signals", [])
        forecast_str += f"""
FORECAST SUMMARY (Next {summary.get('days_available', 7)} days):
Highest Temp: {summary.get('highest_temperature')} C
Lowest Temp: {summary.get('lowest_temperature')} C
Total Precipitation: {summary.get('total_precipitation')} mm
Rainiest Day: {summary.get('rainiest_day')}
Max Rain Probability: {summary.get('max_precipitation_probability')}%

AGRICULTURAL WEATHER RISK SIGNALS:
{chr(10).join(f"- {s}" for s in signals) if signals else "None detected."}
"""
    else:
        forecast_str += "FORECAST: UNAVAILABLE\n"

    # Prepare text representation for Gemini
    prompt_text = f"""
OUTPUT LANGUAGE: {language_full} — ALL advisory string values must be in {language_full}.
Language code: {language}
Crop: {crop}
Location: {location.get("region", "Unknown")}

DISEASE SCREENING RESULT (Machine Learning Output):
Status: {status}
"""
    if status == "DISEASE_DETECTED":
        prompt_text += f"""Detected Disease: {diagnosis.get("disease", "Unknown")}
Class Name: {diagnosis.get("class_name", "Unknown")}
Confidence: {diagnosis.get("confidence", 0) * 100:.1f}%
"""
    else:
        prompt_text += f"""Result: No common target disease was detected.
Confidence: {diagnosis.get("confidence", 0) * 100:.1f}%
"""

    prompt_text += f"""
CURRENT WEATHER:
{weather_str}

SATELLITE DATA:
Status: {satellite.get("status", "UNAVAILABLE")}
"""
    if satellite.get("status") == "AVAILABLE":
        prompt_text += f"NDVI: {satellite.get('ndvi')}\nDays since observation: {satellite.get('days_since')}\nCloud Cover: {satellite.get('cloud_cover')}%\n"

    if satellite.get("status") != "AVAILABLE":
        prompt_text += "\nCRITICAL: If satellite data is unavailable, state that satellite data is unavailable. Never estimate or invent an NDVI value."

    if weather_status != "AVAILABLE":
        prompt_text += "\nCRITICAL: Current weather data is unavailable. Do not invent temperature, humidity, precipitation, rainfall, or weather conditions. Avoid weather-specific advice that depends on missing values."
        
    if weather_forecast.get("status") != "AVAILABLE":
        prompt_text += "\nCRITICAL: The upcoming weather forecast is unavailable. Do not invent future temperature, rainfall, precipitation probability, storms, dry spells, or future weather conditions."
    else:
        prompt_text += f"{forecast_str}"

    # Final mandatory language override — appended LAST so Gemini sees it immediately before generating
    prompt_text += f"""

=== FINAL MANDATORY OUTPUT LANGUAGE REMINDER ===
You MUST write ALL advisory text values in {language_full}.
Do NOT write any advisory sentence or bullet point in English if the requested language is not English.
The JSON keys remain in English. Only the string VALUES must be in {language_full}.
If you are generating in Hindi or Marathi, use natural colloquial farmer-friendly language, not a word-for-word literal translation.
Do not invent or alter any numbers, units, or measurements.
=== END ==="""

    system_instruction = f"""=== MANDATORY OUTPUT LANGUAGE: {language_full} ===
EVERY human-readable string value in the JSON response MUST be written in {language_full}.
This is a non-negotiable hard requirement. Do NOT generate any advisory text in English if the language is not English.
The JSON keys (summary, what_it_means, symptoms, etc.) must remain in English for API compatibility.
Only the string VALUES must be in {language_full}.
The field descriptions in the schema are structural guides only — they do NOT define the output language.
=== END OF LANGUAGE REQUIREMENT ===

You are an agricultural advisory assistant helping farmers interpret an AI-assisted crop disease screening result for KrushiSense.

The disease classification has already been performed by a dedicated machine-learning model (CNN).
You MUST NOT independently diagnose a different disease or guess a disease based on weather/NDVI.
Use ONLY the provided verified diagnosis. Explain the result in simple, practical, farmer-friendly language appropriate for {language_full}-speaking farmers.

If the screening status is HEALTHY:
- Do not claim the crop is "guaranteed" to be disease-free.
- Use wording such as: "No common target disease was detected by the AI screening model."
- Focus on monitoring, crop hygiene, scouting, and sustainable preventive practices.

If the screening status is DISEASE_DETECTED:
- Explain what the detected disease means and typical symptoms.
- Recommend cultural, biological, sanitation, monitoring, irrigation, drainage, and other low-risk management practices.
- Do NOT provide exact synthetic pesticide or chemical dosage instructions.
- If chemical intervention may be necessary, explicitly advise the farmer to consult a qualified local agricultural expert/KVK and follow locally approved product labels.
- Do not invent missing information. Clearly communicate uncertainty. This is an AI-assisted screening tool, not a definitive diagnosis.

Prefer sustainable and regenerative agricultural practices where appropriate.
If weather or satellite information is unavailable, explicitly state that it is unavailable in {language_full} rather than guessing.

NUMERIC DATA PRESERVATION RULES (apply regardless of language):
- Preserve all numerical values exactly as provided: confidence percentages, temperature, precipitation, NDVI, dates, units.
- Do not alter, invent, round, or omit any numeric measurement.
- Units (C, mm, %) must be preserved as-is.

Return ONLY the strictly structured JSON response with all string values in {language_full}."""

    try:
        client = genai.Client(api_key=api_key)
        
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "summary": {"type": "STRING", "description": "Short explanation of the screening result."},
                "what_it_means": {"type": "STRING", "description": "Simple explanation of the detected disease, or crop health monitoring for healthy results."},
                "symptoms": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Typical symptoms to look out for."
                },
                "immediate_actions": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Immediate practical actions."
                },
                "sustainable_practices": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Long-term sustainable management practices."
                },
                "prevention": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Preventive measures for the future."
                },
                "weather_considerations": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Advice based on the provided weather/forecast data."
                },
                "when_to_seek_help": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Situations requiring expert assistance."
                },
                "cautions": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                    "description": "Important safety cautions, especially regarding chemical treatments."
                }
            },
            "required": ["summary", "what_it_means", "symptoms", "immediate_actions", "sustainable_practices", "prevention", "weather_considerations", "when_to_seek_help", "cautions"]
        }

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.2,
            ),
        )
        
        advisory_data = json.loads(response.text)
        
        return JsonResponse({
            "success": True,
            "status": "ADVISORY_GENERATED",
            "advisory": advisory_data
        })

    except Exception as e:
        logger.error(f"Disease Advisory Gemini API Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "success": False,
            "status": "AI_UNAVAILABLE",
            "message": "AI disease advisory is temporarily unavailable."
        })

if __name__ == "__main__":
    model_path = Path(__file__).resolve().parent / "models" / "crop_recommendation_model.pkl"
    model = joblib.load(model_path)
    test_inputs = [
        [90, 42, 43, 20, 80, 6.5, 200],
        [20, 20, 20, 25, 60, 7, 50]
    ]
    for i, inp in enumerate(test_inputs):
        pred = model.predict([inp])[0]
        print(f"Test input {i+1}: {inp} => Predicted crop: {pred}")
