import pytest
from datetime import datetime
from pydantic import ValidationError
from predictions.interoperability.schemas import (
    AgriculturalObservation, ContextSchema, EnvironmentSchema, Measurement,
    ForecastSchema, SatelliteSchema, CropPredictionSchema, DiseaseScreeningSchema, ProvenanceSchema
)
from predictions.interoperability.adapters import build_provenance, adapt_satellite, adapt_environment

def test_weather_provenance():
    env = EnvironmentSchema(temperature_c=Measurement(value=25, unit="C", source="test"))
    prov = build_provenance(env=env)
    assert len(prov) == 1
    assert prov[0].source_id == "open_meteo_current"
    assert prov[0].provider == "Open-Meteo"
    assert prov[0].freshness_category == "CURRENT"
    assert prov[0].observed_at is None

def test_forecast_provenance():
    fcst = ForecastSchema()
    prov = build_provenance(fcst=fcst)
    assert len(prov) == 1
    assert prov[0].source_id == "open_meteo_forecast"
    assert prov[0].provider == "Open-Meteo"
    assert prov[0].freshness_category == "FORECAST"
    assert prov[0].observed_at is None

def test_satellite_provenance():
    now = datetime.utcnow()
    sat = SatelliteSchema(value=0.5, observed_at=now, source="Sentinel-2 L2A", days_since_observation=1)
    prov = build_provenance(sat=sat)
    assert len(prov) == 1
    assert prov[0].source_id == "sentinel-2-l2a"
    assert prov[0].provider == "Sentinel Hub"
    assert prov[0].freshness_category == "LATEST_OBSERVATION"
    assert prov[0].observed_at == now

def test_crop_provenance():
    crop = CropPredictionSchema(crop_canonical="rice", confidence=0.9, prediction_status="ok", data_familiarity="high", model_version="v1")
    prov = build_provenance(crop_pred=crop)
    assert len(prov) == 1
    assert prov[0].source_id == "krushisense_crop_model"
    assert prov[0].provider == "KrushiSense"
    assert prov[0].freshness_category == "MODEL_PREDICTION"
    assert prov[0].model_version == "v1"

def test_disease_provenance():
    disease = DiseaseScreeningSchema(crop="apple", disease="scab", confidence=0.8, status="DISEASE_DETECTED")
    prov = build_provenance(disease=disease)
    assert len(prov) == 1
    assert prov[0].source_id == "krushisense_disease_model"
    assert prov[0].provider == "KrushiSense"
    assert prov[0].freshness_category == "MODEL_PREDICTION"
    assert prov[0].model_version is None

def test_missing_timestamp_not_replaced():
    # If open meteo current returns no timestamp, adapt_environment should keep observed_at None
    env = adapt_environment({"temperature": 25})
    assert env.temperature_c.observed_at is None

def test_satellite_uses_actual_date():
    resp = {
        "success": True,
        "value": 0.5,
        "date_acquired": "2026-08-20T12:00:00Z"
    }
    sat = adapt_satellite(resp)
    assert sat.observed_at is not None
    assert sat.observed_at.year == 2026
    assert sat.observed_at.month == 8

def test_invalid_freshness_rejected():
    with pytest.raises(ValidationError):
        ProvenanceSchema(source_id="test", provider="test", freshness_category="INVALID")
