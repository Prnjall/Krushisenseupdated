from typing import Dict, Any, Optional, List
from datetime import datetime

from .schemas import (
    AgriculturalObservation, ContextSchema, SoilSchema, Measurement,
    EnvironmentSchema, SatelliteSchema, CropPredictionSchema,
    DiseaseScreeningSchema, ForecastSchema, DailyForecast, ProvenanceSchema
)

def adapt_context(
    region: Optional[str] = None,
    country: Optional[str] = None,
    language: str = "en",
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> ContextSchema:
    return ContextSchema(
        region=region,
        country=country,
        language=language,
        lat=lat,
        lon=lon
    )

def adapt_soil_inputs(inputs: Dict[str, Any]) -> Optional[SoilSchema]:
    if not inputs:
        return None
    
    def _get_measurement(key: str) -> Optional[Measurement]:
        val = inputs.get(key)
        if val is None:
            return None
        return Measurement(value=float(val), unit="UNIT_NOT_VERIFIED" if key != "ph" else "pH", source="user_input")

    n = _get_measurement("nitrogen")
    p = _get_measurement("phosphorus")
    k = _get_measurement("potassium")
    ph = _get_measurement("ph")
    
    if n is None and p is None and k is None and ph is None:
        return None

    return SoilSchema(nitrogen=n, phosphorus=p, potassium=k, ph=ph)

def adapt_crop_prediction(response: Dict[str, Any]) -> Optional[CropPredictionSchema]:
    if not response or not response.get("success"):
        return None
        
    return CropPredictionSchema(
        crop_canonical=response.get("prediction", "unknown"),
        confidence=float(response.get("confidence", 0.0)),
        prediction_status=response.get("prediction_status", "unknown"),
        data_familiarity=response.get("data_familiarity", "unknown"),
        model_version=None
    )

def adapt_environment(weather_data: Dict[str, Any]) -> Optional[EnvironmentSchema]:
    if not weather_data:
        return None
        
    temp = weather_data.get("temperature")
    hum = weather_data.get("humidity")
    precip = weather_data.get("current_precipitation")
    
    if temp is None and hum is None and precip is None:
        return None

    def _make(val, unit):
        return Measurement(value=float(val), unit=unit, source="open_meteo_current", observed_at=None) if val is not None else None

    return EnvironmentSchema(
        temperature_c=_make(temp, "C"),
        humidity_percent=_make(hum, "percent"),
        precipitation_mm=_make(precip, "mm")
    )

def adapt_forecast(forecast_list: List[Dict[str, Any]], risk_signals: List[str] = None) -> Optional[ForecastSchema]:
    if not forecast_list:
        return None

    daily_forecasts = []
    for day in forecast_list:
        daily_forecasts.append(
            DailyForecast(
                date=day.get("date", ""),
                temperature_max_c=day.get("temperature_max"),
                temperature_min_c=day.get("temperature_min"),
                precipitation_mm=day.get("precipitation_sum"),
                precipitation_probability_percent=day.get("precipitation_probability"),
                weather_code=day.get("weather_code")
            )
        )
        
    return ForecastSchema(
        horizon_days=len(daily_forecasts),
        daily_forecasts=daily_forecasts,
        risk_signals=risk_signals or []
    )

def adapt_satellite(response: Dict[str, Any]) -> Optional[SatelliteSchema]:
    if not response or not response.get("success") or response.get("status") in ["NO_RECENT_DATA", "INVALID_DATA", "SERVER_ERROR"]:
        return None
        
    val = response.get("value")
    if val is None:
        return None

    date_str = response.get("date_acquired")
    observed_at = None
    if date_str:
        try:
            observed_at = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception:
            pass

    return SatelliteSchema(
        indicator=response.get("indicator", "NDVI"),
        value=float(val),
        unit="index",
        observed_at=observed_at,
        cloud_cover_percent=response.get("cloud_cover_percentage"),
        source=response.get("source", "Sentinel-2 L2A"),
        days_since_observation=response.get("days_since_observation", 0)
    )

def adapt_disease_screening(response: Dict[str, Any]) -> Optional[DiseaseScreeningSchema]:
    if not response or not response.get("success") or response.get("status") in ["ANALYSIS_UNAVAILABLE", "UNSUPPORTED_CROP", "INVALID_IMAGE"]:
        return None
        
    diag = response.get("diagnosis", {})
    if not diag and response.get("status") == "LOW_CONFIDENCE":
        return DiseaseScreeningSchema(
            crop=response.get("crop", "unknown"),
            disease="unknown",
            confidence=float(response.get("confidence", 0.0)),
            status="LOW_CONFIDENCE"
        )
        
    return DiseaseScreeningSchema(
        crop=response.get("crop", "unknown"),
        disease=diag.get("class_name", "unknown"),
        confidence=float(diag.get("confidence", 0.0)),
        status=response.get("status", "unknown")
    )

def build_provenance(
    env: Optional[EnvironmentSchema] = None,
    fcst: Optional[ForecastSchema] = None,
    sat: Optional[SatelliteSchema] = None,
    crop_pred: Optional[CropPredictionSchema] = None,
    disease: Optional[DiseaseScreeningSchema] = None
) -> List[ProvenanceSchema]:
    prov = []
    if env:
        prov.append(ProvenanceSchema(source_id="open_meteo_current", provider="Open-Meteo", freshness_category="CURRENT", observed_at=None))
    if fcst:
        prov.append(ProvenanceSchema(source_id="open_meteo_forecast", provider="Open-Meteo", freshness_category="FORECAST", observed_at=None))
    if sat:
        prov.append(ProvenanceSchema(source_id="sentinel-2-l2a", provider="Sentinel Hub", freshness_category="LATEST_OBSERVATION", observed_at=sat.observed_at))
    if crop_pred:
        prov.append(ProvenanceSchema(source_id="krushisense_crop_model", provider="KrushiSense", freshness_category="MODEL_PREDICTION", model_version=crop_pred.model_version))
    if disease:
        prov.append(ProvenanceSchema(source_id="krushisense_disease_model", provider="KrushiSense", freshness_category="MODEL_PREDICTION", model_version=disease.model_version))
    return prov

def build_agricultural_observation(
    context_kwargs: Dict[str, Any] = None,
    crop_inputs: Dict[str, Any] = None,
    crop_response: Dict[str, Any] = None,
    weather_response: Dict[str, Any] = None,
    satellite_response: Dict[str, Any] = None,
    disease_response: Dict[str, Any] = None
) -> AgriculturalObservation:
    
    ctx = adapt_context(**(context_kwargs or {}))
    soil = adapt_soil_inputs(crop_inputs or {})
    crop_pred = adapt_crop_prediction(crop_response or {})
    
    env = None
    fcst = None
    if weather_response and weather_response.get("success"):
        env = adapt_environment(weather_response.get("weather", {}))
        fcst = adapt_forecast(weather_response.get("forecast", []), weather_response.get("risk_signals", []))
        
    sat = adapt_satellite(satellite_response or {})
    disease = adapt_disease_screening(disease_response or {})
    
    prov = build_provenance(
        env=env,
        fcst=fcst,
        sat=sat,
        crop_pred=crop_pred,
        disease=disease
    )
    
    return AgriculturalObservation(
        context=ctx,
        soil=soil,
        environment=env,
        forecast=fcst,
        satellite=sat,
        crop_prediction=crop_pred,
        disease_screening=disease,
        provenance=prov
    )
