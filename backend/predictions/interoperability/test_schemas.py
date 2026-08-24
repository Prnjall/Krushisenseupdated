import pytest
from pydantic import ValidationError
from datetime import datetime
from predictions.interoperability.schemas import (
    AgriculturalObservation, ContextSchema, SoilSchema, Measurement,
    EnvironmentSchema, SatelliteSchema, CropPredictionSchema,
    DiseaseScreeningSchema
)

def test_complete_observation():
    obs = AgriculturalObservation(
        context=ContextSchema(region="Nashik", country="India", language="mr"),
        soil=SoilSchema(
            nitrogen=Measurement(value=90, unit="UNIT_NOT_VERIFIED", source="user_input"),
            ph=Measurement(value=6.5, unit="pH", source="user_input")
        ),
        environment=EnvironmentSchema(
            temperature_c=Measurement(value=26.5, unit="C", source="open_meteo"),
            humidity_percent=Measurement(value=72, unit="percent", source="open_meteo"),
            precipitation_mm=Measurement(value=12.0, unit="mm", source="open_meteo")
        ),
        satellite=SatelliteSchema(
            value=0.54, observed_at=datetime.utcnow(), source="sentinel-2", days_since_observation=2
        ),
        crop_prediction=CropPredictionSchema(
            crop_canonical="rice", confidence=0.89, prediction_status="high_confidence", data_familiarity="high"
        )
    )
    assert obs.schema_version == "1.0"
    assert obs.context.region == "Nashik"

def test_soil_only_observation():
    obs = AgriculturalObservation(
        context=ContextSchema(),
        soil=SoilSchema(nitrogen=Measurement(value=45, unit="UNIT_NOT_VERIFIED", source="sensor"))
    )
    assert obs.soil is not None
    assert obs.environment is None

def test_weather_only_observation():
    obs = AgriculturalObservation(
        context=ContextSchema(),
        environment=EnvironmentSchema(temperature_c=Measurement(value=20, unit="C", source="sensor"))
    )
    assert obs.environment is not None

def test_satellite_only_observation():
    obs = AgriculturalObservation(
        context=ContextSchema(),
        satellite=SatelliteSchema(value=0.2, observed_at=datetime.utcnow(), source="sentinel", days_since_observation=1)
    )
    assert obs.satellite is not None

def test_crop_prediction_only():
    obs = AgriculturalObservation(
        context=ContextSchema(),
        crop_prediction=CropPredictionSchema(crop_canonical="maize", confidence=0.7, prediction_status="moderate", data_familiarity="moderate")
    )
    assert obs.crop_prediction is not None

def test_disease_result_only():
    obs = AgriculturalObservation(
        context=ContextSchema(),
        disease_screening=DiseaseScreeningSchema(crop="apple", disease="apple_scab", confidence=0.9, status="DISEASE_DETECTED")
    )
    assert obs.disease_screening is not None

def test_partial_observation():
    obs = AgriculturalObservation(
        context=ContextSchema(),
        soil=SoilSchema(),
        crop_prediction=CropPredictionSchema(crop_canonical="rice", confidence=0.8, prediction_status="ok", data_familiarity="ok")
    )
    assert obs.satellite is None

def test_invalid_confidence_greater_than_1():
    with pytest.raises(ValidationError):
        CropPredictionSchema(crop_canonical="rice", confidence=1.5, prediction_status="ok", data_familiarity="ok")

def test_invalid_confidence_less_than_0():
    with pytest.raises(ValidationError):
        DiseaseScreeningSchema(crop="apple", disease="apple_scab", confidence=-0.1, status="DISEASE_DETECTED")

def test_invalid_ndvi_greater_than_1():
    with pytest.raises(ValidationError):
        SatelliteSchema(value=1.5, observed_at=datetime.utcnow(), source="sentinel", days_since_observation=1)

def test_invalid_ndvi_less_than_minus_1():
    with pytest.raises(ValidationError):
        SatelliteSchema(value=-1.1, observed_at=datetime.utcnow(), source="sentinel", days_since_observation=1)

def test_invalid_humidity_greater_than_100():
    with pytest.raises(ValidationError):
        EnvironmentSchema(humidity_percent=Measurement(value=105, unit="%", source="sensor"))

def test_missing_optional_fields():
    obs = AgriculturalObservation(context=ContextSchema())
    # Should not raise exception
    assert obs.environment is None
    assert obs.satellite is None
    assert obs.disease_screening is None
