from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime

class ContextSchema(BaseModel):
    region: Optional[str] = None
    country: Optional[str] = None
    language: str = "en"
    # GPS coordinates are intentionally optional and marked as privacy-sensitive
    lat: Optional[float] = Field(None, description="Privacy-sensitive GPS latitude")
    lon: Optional[float] = Field(None, description="Privacy-sensitive GPS longitude")

class Measurement(BaseModel):
    value: float
    unit: str
    source: str
    observed_at: Optional[datetime] = None

class SoilSchema(BaseModel):
    # Units are explicitly NOT VERIFIED based on the baseline dataset audit.
    # We enforce 'UNIT_NOT_VERIFIED' as the default/expected string if unknown.
    nitrogen: Optional[Measurement] = None
    phosphorus: Optional[Measurement] = None
    potassium: Optional[Measurement] = None
    ph: Optional[Measurement] = None
    
    @field_validator('ph')
    @classmethod
    def check_ph(cls, v: Optional[Measurement]):
        if v is not None and not (0 <= v.value <= 14):
            raise ValueError("pH must be between 0 and 14")
        return v

class EnvironmentSchema(BaseModel):
    temperature_c: Optional[Measurement] = None
    humidity_percent: Optional[Measurement] = None
    precipitation_mm: Optional[Measurement] = None

    @field_validator('humidity_percent')
    @classmethod
    def check_humidity(cls, v: Optional[Measurement]):
        if v is not None and not (0 <= v.value <= 100):
            raise ValueError("Humidity must be between 0 and 100")
        return v

    @field_validator('temperature_c')
    @classmethod
    def check_temp(cls, v: Optional[Measurement]):
        # Consistent with existing /api/predict-crop/ validation
        if v is not None and not (-50 <= v.value <= 60):
            raise ValueError("Temperature must be within sensible bounds (-50 to 60 °C)")
        return v

class DailyForecast(BaseModel):
    date: str
    temperature_max_c: Optional[float] = None
    temperature_min_c: Optional[float] = None
    precipitation_mm: Optional[float] = None
    precipitation_probability_percent: Optional[float] = None
    weather_code: Optional[int] = None

class ForecastSchema(BaseModel):
    horizon_days: int = 7
    daily_forecasts: List[DailyForecast] = []
    risk_signals: List[str] = []

class SatelliteSchema(BaseModel):
    indicator: str = "NDVI"
    value: float
    unit: str = "unitless"
    observed_at: Optional[datetime] = None
    cloud_cover_percent: Optional[float] = None
    source: str
    days_since_observation: int

    @field_validator('value')
    @classmethod
    def check_ndvi(cls, v: float):
        if not (-1 <= v <= 1):
            raise ValueError("NDVI must be between -1 and 1")
        return v

class CropPredictionSchema(BaseModel):
    model_config = {"protected_namespaces": ()}
    crop_canonical: str
    confidence: float
    prediction_status: str
    data_familiarity: str
    model_version: Optional[str] = None

    @field_validator('confidence')
    @classmethod
    def check_confidence(cls, v: float):
        if not (0 <= v <= 1):
            raise ValueError("Confidence must be a decimal between 0 and 1")
        return v

class DiseaseScreeningSchema(BaseModel):
    model_config = {"protected_namespaces": ()}
    crop: str
    disease: str
    confidence: float
    status: str
    model_version: Optional[str] = None

    @field_validator('confidence')
    @classmethod
    def check_confidence(cls, v: float):
        if not (0 <= v <= 1):
            raise ValueError("Confidence must be a decimal between 0 and 1")
        return v

class ProvenanceSchema(BaseModel):
    model_config = {"protected_namespaces": ()}
    source_id: str
    provider: str
    observed_at: Optional[datetime] = None
    freshness_category: Literal['CURRENT', 'FORECAST', 'LATEST_OBSERVATION', 'STATIC_DATASET', 'MODEL_PREDICTION', 'AI_GENERATED']
    model_version: Optional[str] = None

class AgriculturalObservation(BaseModel):
    """
    The canonical root object for all agricultural data exchange in KrushiSense.
    Supports partial contexts (e.g. only soil, or only weather).
    """
    schema_version: str = "1.0"
    context: ContextSchema
    soil: Optional[SoilSchema] = None
    environment: Optional[EnvironmentSchema] = None
    forecast: Optional[ForecastSchema] = None
    satellite: Optional[SatelliteSchema] = None
    crop_prediction: Optional[CropPredictionSchema] = None
    disease_screening: Optional[DiseaseScreeningSchema] = None
    provenance: List[ProvenanceSchema] = []
