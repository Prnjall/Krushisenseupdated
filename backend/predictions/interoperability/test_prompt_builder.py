import pytest
from predictions.interoperability.schemas import AgriculturalObservation
from predictions.interoperability.prompt_builder import build_interop_prompt, get_interop_system_instruction

def get_base_obs_dict():
    return {
        "schema_version": "1.0",
        "context": {
            "lat": 18.5204,
            "lon": 73.8567,
            "region": "Maharashtra",
            "country": "India",
            "language": "en"
        }
    }

def test_prompt_language_en_hi_mr():
    # Q. Language en/hi/mr
    for lang in ["en", "hi", "mr"]:
        obs_dict = get_base_obs_dict()
        obs_dict["context"]["language"] = lang
        obs = AgriculturalObservation(**obs_dict)
        prompt = build_interop_prompt(obs)
        assert f"Language requested: {lang}" in prompt

def test_prompt_no_gps():
    # R. GPS coordinates absent from Gemini prompt
    obs_dict = get_base_obs_dict()
    obs_dict["context"]["lat"] = 12.3456
    obs_dict["context"]["lon"] = 78.9101
    obs = AgriculturalObservation(**obs_dict)
    prompt = build_interop_prompt(obs)
    assert "12.3456" not in prompt
    assert "78.9101" not in prompt
    assert "lat" not in prompt.lower().split("location:")[0] # Check it's not explicitly in the location line or before
    assert "lon" not in prompt.lower().split("location:")[0]

def test_missing_data_blocks():
    # H. Missing weather
    # I. Missing satellite
    # J. Missing crop prediction
    # K. Missing disease screening
    obs = AgriculturalObservation(**get_base_obs_dict())
    prompt = build_interop_prompt(obs)
    assert "SOIL DATA: UNAVAILABLE" in prompt
    assert "CURRENT WEATHER: UNAVAILABLE" in prompt
    assert "FORECAST SUMMARY: UNAVAILABLE" in prompt
    assert "SATELLITE DATA: UNAVAILABLE" in prompt
    assert "CROP PREDICTION: UNAVAILABLE" in prompt
    assert "DISEASE SCREENING: UNAVAILABLE" in prompt

def test_soil_only_and_safety():
    # B. Soil-only context
    # L. UNIT_NOT_VERIFIED safety
    obs_dict = get_base_obs_dict()
    obs_dict["soil"] = {
        "nitrogen": {"value": 10.0, "unit": "mg/kg", "source": "sensor_x"},
        "phosphorus": {"value": 20.0, "unit": "mg/kg", "source": "sensor_x"},
        "potassium": {"value": 30.0, "unit": "mg/kg", "source": "sensor_x"},
        "ph": {"value": 6.5, "unit": "pH", "source": "sensor_x"}
    }
    obs = AgriculturalObservation(**obs_dict)
    prompt = build_interop_prompt(obs)
    assert "Nitrogen (N): 10.0" in prompt
    assert "pH: 6.5" in prompt
    assert "Units: UNIT_NOT_VERIFIED" in prompt
    assert "N/P/K units are UNIT_NOT_VERIFIED" in prompt
    
    assert "CURRENT WEATHER: UNAVAILABLE" in prompt

def test_weather_and_forecast_only():
    # C. Weather-only context
    # M. Forecast vs CURRENT distinction
    obs_dict = get_base_obs_dict()
    obs_dict["environment"] = {
        "temperature_c": {"value": 25.5, "unit": "C", "source": "local_station"},
        "humidity_percent": {"value": 60.0, "unit": "%", "source": "local_station"}
    }
    obs_dict["forecast"] = {
        "horizon_days": 7,
        "daily_forecasts": [{"date": "2026-08-20", "temperature_max_c": 26.0}],
        "risk_signals": ["Expected dry spell"]
    }
    obs = AgriculturalObservation(**obs_dict)
    prompt = build_interop_prompt(obs)
    
    assert "CURRENT WEATHER (FRESHNESS: CURRENT):" in prompt
    assert "Temperature: 25.5 C" in prompt
    
    assert "FORECAST SUMMARY (FRESHNESS: FORECAST):" in prompt
    assert "Expected dry spell" in prompt
    
    assert "Forecast data must not be described as observed current weather" in prompt

def test_satellite_only_and_ndvi_safety():
    # D. Satellite-only context
    # N. NDVI freshness distinction
    obs_dict = get_base_obs_dict()
    obs_dict["satellite"] = {
        "indicator": "NDVI",
        "value": 0.65,
        "observed_at": "2026-08-15T10:00:00Z",
        "days_since_observation": 5,
        "cloud_cover_percent": 10.5,
        "source": "Sentinel-2"
    }
    obs = AgriculturalObservation(**obs_dict)
    prompt = build_interop_prompt(obs)
    
    assert "SATELLITE DATA (FRESHNESS: LATEST_OBSERVATION):" in prompt
    assert "Value: 0.65" in prompt
    assert "Days since observation: 5" in prompt
    assert "NDVI must not be described as real-time" in prompt

def test_crop_only_and_model_distinction():
    # E. Crop-only context
    # O. Model prediction distinction
    obs_dict = get_base_obs_dict()
    obs_dict["crop_prediction"] = {
        "crop_canonical": "wheat",
        "confidence": 0.85,
        "prediction_status": "RECOMMENDED",
        "data_familiarity": "HIGH",
        "model_version": "v2.1"
    }
    obs = AgriculturalObservation(**obs_dict)
    prompt = build_interop_prompt(obs)
    
    assert "CROP PREDICTION (FRESHNESS: MODEL_PREDICTION):" in prompt
    assert "Primary Recommendation: wheat" in prompt
    assert "Model predictions must be described as model outputs, not ground truth" in prompt
    assert "Do NOT replace the crop prediction model" in prompt

def test_disease_only_and_safety():
    # F. Disease-only context
    # P. Disease LOW_CONFIDENCE safety
    obs_dict = get_base_obs_dict()
    obs_dict["disease_screening"] = {
        "crop": "apple",
        "disease": "Apple Scab",
        "confidence": 0.95,
        "status": "DISEASE_DETECTED"
    }
    obs = AgriculturalObservation(**obs_dict)
    prompt = build_interop_prompt(obs)
    
    assert "DISEASE SCREENING (FRESHNESS: MODEL_PREDICTION):" in prompt
    assert "Diagnosis: Apple Scab" in prompt
    assert "Treat the CNN output as the supplied screening result" in prompt
    assert "For LOW_CONFIDENCE, UNSUPPORTED_CROP, or INVALID_IMAGE, do not generate disease-specific treatment advice" in prompt

def test_full_context():
    # A. / G. Full context
    obs_dict = get_base_obs_dict()
    obs_dict["soil"] = {"ph": {"value": 7.0, "unit": "pH", "source": "s"}}
    obs_dict["environment"] = {"temperature_c": {"value": 25.0, "unit": "C", "source": "s"}}
    obs_dict["forecast"] = {"horizon_days": 7, "daily_forecasts": []} # no daily forecasts means unavailable? Wait, rule says if obs.forecast.daily_forecasts...
    obs_dict["forecast"]["daily_forecasts"].append({"date": "2026-08-20", "temperature_max_c": 26.0})
    obs_dict["satellite"] = {"indicator": "NDVI", "value": 0.5, "days_since_observation": 1, "source": "s"}
    obs_dict["crop_prediction"] = {"crop_canonical": "rice", "confidence": 0.9, "prediction_status": "OK", "data_familiarity": "HIGH"}
    obs_dict["disease_screening"] = {"crop": "rice", "disease": "healthy", "confidence": 0.99, "status": "HEALTHY"}
    
    obs = AgriculturalObservation(**obs_dict)
    prompt = build_interop_prompt(obs)
    
    assert "SOIL DATA:\n" in prompt
    assert "CURRENT WEATHER (FRESHNESS: CURRENT):\n" in prompt
    assert "FORECAST SUMMARY (FRESHNESS: FORECAST):\n" in prompt
    assert "SATELLITE DATA (FRESHNESS: LATEST_OBSERVATION):\n" in prompt
    assert "CROP PREDICTION (FRESHNESS: MODEL_PREDICTION):\n" in prompt
    assert "DISEASE SCREENING (FRESHNESS: MODEL_PREDICTION):\n" in prompt
    
    assert "SOIL DATA: UNAVAILABLE" not in prompt
    assert "CURRENT WEATHER: UNAVAILABLE" not in prompt
    assert "FORECAST SUMMARY: UNAVAILABLE" not in prompt
    assert "SATELLITE DATA: UNAVAILABLE" not in prompt
    assert "CROP PREDICTION: UNAVAILABLE" not in prompt
    assert "DISEASE SCREENING: UNAVAILABLE" not in prompt

def test_no_api_key_in_prompt():
    # S. No API key in generated prompt
    obs = AgriculturalObservation(**get_base_obs_dict())
    prompt = build_interop_prompt(obs)
    sys_inst = get_interop_system_instruction()
    # It's physically impossible for the key to be in the prompt without explicitly adding it, 
    # but we can assert basic sanity
    assert "test_key" not in prompt
    assert "API_KEY" not in prompt
    assert "test_key" not in sys_inst
    assert "API_KEY" not in sys_inst
