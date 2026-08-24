from .schemas import AgriculturalObservation
from typing import Dict, Any

def build_interop_prompt(obs: AgriculturalObservation) -> str:
    lang = obs.context.language
    region = obs.context.region or "Unknown region"
    country = obs.context.country or "Unknown country"
    
    prompt = f"Language requested: {lang}\n"
    prompt += f"Location: {region}, {country}\n\n"
    
    # Soil
    if obs.soil:
        prompt += "SOIL DATA:\n"
        if obs.soil.nitrogen is not None:
            prompt += f"Nitrogen (N): {obs.soil.nitrogen.value}\n"
        if obs.soil.phosphorus is not None:
            prompt += f"Phosphorus (P): {obs.soil.phosphorus.value}\n"
        if obs.soil.potassium is not None:
            prompt += f"Potassium (K): {obs.soil.potassium.value}\n"
        if obs.soil.ph is not None:
            prompt += f"pH: {obs.soil.ph.value}\n"
        prompt += "Units: UNIT_NOT_VERIFIED\n"
        if False:
            prompt += f"Source: {obs.soil.source}\n"
        prompt += "\n"
    else:
        prompt += "SOIL DATA: UNAVAILABLE\n\n"
        
    # Environment
    if obs.environment:
        prompt += "CURRENT WEATHER (FRESHNESS: CURRENT):\n"
        if obs.environment.temperature_c is not None:
            prompt += f"Temperature: {obs.environment.temperature_c.value} C\n"
        if obs.environment.humidity_percent is not None:
            prompt += f"Humidity: {obs.environment.humidity_percent.value}%\n"
        if obs.environment.precipitation_mm is not None:
            prompt += f"Precipitation: {obs.environment.precipitation_mm.value} mm\n"
        if False:
            prompt += f"Provenance: {obs.environment.source}\n"
        prompt += "\n"
    else:
        prompt += "CURRENT WEATHER: UNAVAILABLE\n\n"
        
    # Forecast
    if obs.forecast and obs.forecast.daily_forecasts:
        prompt += "FORECAST SUMMARY (FRESHNESS: FORECAST):\n"
        days = obs.forecast.horizon_days
        prompt += f"Horizon: {days} days\n"
        if obs.forecast.risk_signals:
            prompt += "AGRICULTURAL WEATHER RISK SIGNALS:\n"
            for sig in obs.forecast.risk_signals:
                prompt += f"- {sig}\n"
        if False:
            prompt += f"Provenance: {obs.forecast.source}\n"
        prompt += "\n"
    else:
        prompt += "FORECAST SUMMARY: UNAVAILABLE\n\n"
        
    # Satellite
    if obs.satellite:
        prompt += "SATELLITE DATA (FRESHNESS: LATEST_OBSERVATION):\n"
        prompt += f"Indicator: {obs.satellite.indicator}\n"
        prompt += f"Value: {obs.satellite.value}\n"
        prompt += f"Observation Date: {obs.satellite.observed_at}\n"
        prompt += f"Days since observation: {obs.satellite.days_since_observation}\n"
        if obs.satellite.cloud_cover_percent is not None:
            prompt += f"Cloud Cover: {obs.satellite.cloud_cover_percent}%\n"
        if obs.satellite.source:
            prompt += f"Provenance: {obs.satellite.source}\n"
        prompt += "\n"
    else:
        prompt += "SATELLITE DATA: UNAVAILABLE\n\n"
        
    # Crop Prediction
    if obs.crop_prediction:
        prompt += "CROP PREDICTION (FRESHNESS: MODEL_PREDICTION):\n"
        prompt += f"Primary Recommendation: {obs.crop_prediction.crop_canonical}\n"
        prompt += f"Confidence: {obs.crop_prediction.confidence}\n"
        prompt += f"Status: {obs.crop_prediction.prediction_status}\n"
        if obs.crop_prediction.model_version:
            prompt += f"Model Version: {obs.crop_prediction.model_version}\n"
        if False:
            prompt += f"Provenance: {obs.crop_prediction.source}\n"
        prompt += "\n"
    else:
        prompt += "CROP PREDICTION: UNAVAILABLE\n\n"
        
    # Disease Screening
    if obs.disease_screening:
        prompt += "DISEASE SCREENING (FRESHNESS: MODEL_PREDICTION):\n"
        prompt += f"Crop: {obs.disease_screening.crop}\n"
        prompt += f"Diagnosis: {obs.disease_screening.disease}\n"
        prompt += f"Confidence: {obs.disease_screening.confidence}\n"
        prompt += f"Status: {obs.disease_screening.status}\n"
        if obs.disease_screening.model_version:
            prompt += f"Model Version: {obs.disease_screening.model_version}\n"
        if False:
            prompt += f"Provenance: {obs.disease_screening.source}\n"
        prompt += "\n"
    else:
        prompt += "DISEASE SCREENING: UNAVAILABLE\n\n"
        
    # Instructions
    prompt += """CRITICAL INSTRUCTIONS:
- If a data block is marked as UNAVAILABLE, treat it as such. Do not infer or fabricate unavailable measurements, weather conditions, NDVI, crop probabilities, or disease diagnostics.
- FORECAST vs CURRENT: Forecast data must not be described as observed current weather.
- NDVI: NDVI must not be described as real-time. Acknowledge that NDVI is a satellite observation and include appropriate freshness context. Do not claim NDVI alone proves a specific disease.
- MODEL PREDICTIONS: Model predictions must be described as model outputs, not ground truth.
- HISTORICAL: Historical/older satellite observations must retain their actual observation date.
- SOIL SAFETY: N/P/K units are UNIT_NOT_VERIFIED. Therefore, you MUST NOT provide precise fertilizer dosage recommendations based solely on these values. You may provide general nutrient-management guidance. If exact fertilizer dosage is requested, recommend obtaining verified soil-test units and consulting a qualified agricultural expert. Do not assume mg/kg, ppm, or another unit.
- CROP PREDICTION SAFETY: Do NOT replace the crop prediction model. Explain the provided prediction and its context. If confidence is low or familiarity is insufficient, clearly communicate uncertainty. Do not invent a different crop.
- DISEASE SAFETY: Do NOT independently diagnose another disease. Treat the CNN output as the supplied screening result. For LOW_CONFIDENCE, UNSUPPORTED_CROP, or INVALID_IMAGE, do not generate disease-specific treatment advice. If DISEASE_DETECTED, provide general sustainable/cultural management guidance. Do NOT provide precise synthetic pesticide/fungicide dosages. Recommend local agricultural extension/KVK or equivalent expert support for chemical intervention.
- WEATHER RISK: Use deterministic risk signals provided. Translate these signals into practical farmer advice. Do NOT create unsupported universal agricultural thresholds (e.g., do not transform an "Expected dry spell" into an absolute crop-failure claim).
- LANGUAGE: Generate advisory values in the requested language. Scientific disease/crop names may remain in standardized English where appropriate.
"""
    return prompt

def get_interop_system_instruction() -> str:
    return """You are an interoperable agricultural advisory AI for KrushiSense.
Your job is to synthesize Canonical Agricultural Observations into practical, localized, cautious, and evidence-grounded agricultural guidance.
Use ONLY the structured information supplied in the request.
Never invent missing measurements, weather conditions, NDVI, crop probabilities, or disease diagnostics.
Never claim that NDVI alone proves crop health or that a recommendation guarantees yield.
Clearly distinguish observed data from general agricultural guidance.
When data is unavailable, explicitly say it is unavailable in your reasoning.
Give practical recommendations in simple farmer-friendly language.
Prefer sustainable and regenerative agricultural practices where appropriate.
Do not provide dangerous or unsupported pesticide dosage instructions.
Return ONLY the required structured JSON response. Ensure the VALUES of the JSON response are written in the requested language."""
