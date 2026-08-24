import pytest
import sys
sys.path.insert(0, r"P:\Agri Analysis")
from predictions.interoperability.adapters import (
    adapt_context, adapt_soil_inputs, adapt_crop_prediction,
    adapt_environment, adapt_forecast, adapt_satellite,
    adapt_disease_screening, build_agricultural_observation
)

def test_full_crop_prediction():
    resp = {
        "success": True,
        "prediction": "rice",
        "confidence": 0.89,
        "prediction_status": "high_confidence",
        "data_familiarity": "high"
    }
    schema = adapt_crop_prediction(resp)
    assert schema is not None
    assert schema.crop_canonical == "rice"
    assert schema.confidence == 0.89
    assert schema.prediction_status == "high_confidence"

def test_weather_response_environment():
    resp = {
        "temperature": 26.5,
        "humidity": 72,
        "current_precipitation": 12.0
    }
    schema = adapt_environment(resp)
    assert schema is not None
    assert schema.temperature_c.value == 26.5
    assert schema.humidity_percent.value == 72
    assert schema.precipitation_mm.value == 12.0

def test_weather_forecast():
    forecast_list = [{
        "date": "2026-08-20",
        "temperature_max": 28,
        "temperature_min": 24,
        "precipitation_sum": 15,
        "precipitation_probability": 80,
        "weather_code": 3
    }]
    schema = adapt_forecast(forecast_list, ["Rain expected"])
    assert schema is not None
    assert schema.horizon_days == 1
    assert schema.daily_forecasts[0].precipitation_mm == 15
    assert schema.risk_signals == ["Rain expected"]

def test_satellite_response():
    resp = {
        "success": True,
        "indicator": "NDVI",
        "value": 0.54,
        "date_acquired": "2026-08-20T12:00:00Z",
        "cloud_cover_percentage": 10,
        "source": "Sentinel-2 L2A",
        "days_since_observation": 2
    }
    schema = adapt_satellite(resp)
    assert schema is not None
    assert schema.value == 0.54
    assert schema.unit == "index"

def test_satellite_unavailable():
    resp = {
        "success": False,
        "status": "NO_RECENT_DATA"
    }
    schema = adapt_satellite(resp)
    assert schema is None

def test_disease_response():
    resp = {
        "success": True,
        "status": "DISEASE_DETECTED",
        "crop": "apple",
        "diagnosis": {
            "disease": "Apple Scab",
            "class_name": "apple_scab",
            "confidence": 0.94
        }
    }
    schema = adapt_disease_screening(resp)
    assert schema is not None
    assert schema.disease == "apple_scab"
    assert schema.confidence == 0.94

def test_soil_input():
    inputs = {
        "nitrogen": 90, "phosphorus": 42, "potassium": 43, "ph": 6.5,
        "temperature": 20, "humidity": 80, "rainfall": 200
    }
    schema = adapt_soil_inputs(inputs)
    assert schema is not None
    assert schema.nitrogen.value == 90
    assert schema.nitrogen.unit == "UNIT_NOT_VERIFIED"
    assert schema.ph.value == 6.5
    # Should not pick up temperature/humidity
    assert not hasattr(schema, "temperature")

def test_crop_rainfall_not_current_weather():
    inputs = {"rainfall": 200}
    schema = adapt_soil_inputs(inputs)
    assert schema is None # No soil fields present

def test_partial_context():
    obs = build_agricultural_observation(
        context_kwargs={"region": "Pune"},
        crop_inputs={"nitrogen": 50, "ph": 7},
        crop_response={"success": True, "prediction": "wheat"}
    )
    assert obs.context.region == "Pune"
    assert obs.soil.nitrogen.value == 50
    assert obs.crop_prediction.crop_canonical == "wheat"
    assert obs.environment is None
    assert obs.satellite is None
    
def test_complete_context():
    obs = build_agricultural_observation(
        context_kwargs={"region": "Pune"},
        crop_inputs={"nitrogen": 50, "ph": 7},
        crop_response={"success": True, "prediction": "wheat"},
        weather_response={"success": True, "weather": {"temperature": 25}, "forecast": [{"date": "today"}]},
        satellite_response={"success": True, "value": 0.5},
        disease_response={"success": True, "status": "HEALTHY", "diagnosis": {"class_name": "healthy", "confidence": 0.99}}
    )
    assert obs.environment.temperature_c.value == 25
    assert obs.satellite.value == 0.5
    assert obs.disease_screening.status == "HEALTHY"
    # Provenance tests
    prov_sources = [p.source_id for p in obs.provenance]
    assert "open_meteo_current" in prov_sources
    assert "sentinel-2-l2a" in prov_sources
    assert "krushisense_crop_model" in prov_sources
    assert "krushisense_disease_model" in prov_sources

def test_missing_optional_weather_and_satellite():
    obs = build_agricultural_observation()
    assert obs.environment is None
    assert obs.satellite is None

def test_invalid_confidence_rejected():
    resp = {
        "success": True,
        "prediction": "rice",
        "confidence": 1.5,
        "prediction_status": "high_confidence"
    }
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        adapt_crop_prediction(resp)

def test_invalid_ndvi_rejected():
    resp = {
        "success": True,
        "value": -1.5,
        "date_acquired": "2026-08-20T12:00:00Z"
    }
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        adapt_satellite(resp)

def test_gps_not_logged(capsys):
    obs = build_agricultural_observation(context_kwargs={"lat": 18.5204, "lon": 73.8567})
    # The adapter should just assign it, not print it
    out, err = capsys.readouterr()
    assert "18.5204" not in out
    assert obs.context.lat == 18.5204
