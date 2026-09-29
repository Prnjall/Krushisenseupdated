import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)

# Heuristics based on general agronomic principles
LEGUMES = {
    'blackgram', 'chickpea', 'gram', 'kidneybeans', 'lentil', 
    'masoor', 'moong', 'mothbeans', 'mungbean', 'pigeonpeas', 
    'soybean', 'tur', 'urad'
}

WATER_INTENSIVE = {
    'rice', 'sugarcane', 'cotton', 'jute', 'banana', 'papaya'
}

DROUGHT_TOLERANT = {
    'jowar', 'mothbeans', 'chickpea', 'moong', 'gram'
}

def calculate_regenerative_score(
    crop: str,
    soil_context: Dict[str, float],
    weather_context: Dict[str, Any],
    ndvi_context: Dict[str, Any],
    base_probability: float
) -> Tuple[float, List[str]]:
    """
    Calculates a regenerative adjustment score for a given crop.
    Returns (adjustment_score, list_of_reasons).
    The adjustment score is bounded [-0.15, +0.15] so it acts as a heuristic nudge,
    not a complete override of the ML model.
    """
    score = 0.0
    reasons = []
    
    crop_lower = crop.lower()
    
    # 1. Soil Health (Nitrogen depletion)
    n_val = soil_context.get('N')
    if n_val is not None:
        try:
            n_val = float(n_val)
            if n_val < 40.0:  # Low Nitrogen heuristic
                if crop_lower in LEGUMES:
                    score += 0.05
                    reasons.append("Soil signal (Nitrogen): Legumes fix atmospheric nitrogen and are well-suited for low-N environments.")
                elif crop_lower in WATER_INTENSIVE:
                    score -= 0.02
                    reasons.append("Soil signal (Nitrogen): Crop demands high nutrient input, which may be challenging in low-N conditions.")
        except (ValueError, TypeError):
            pass
            
    # 2. Water / Climate Risk
    # Check rainfall or weather forecast risk signals
    rainfall = soil_context.get('rainfall')  # Historical/Annual rainfall provided to ML
    if rainfall is not None:
        try:
            rainfall = float(rainfall)
            if rainfall < 100.0:  # Low rainfall heuristic
                if crop_lower in WATER_INTENSIVE:
                    score -= 0.08
                    reasons.append("Water-risk consideration: This water-intensive crop is risky given low historical rainfall.")
                elif crop_lower in DROUGHT_TOLERANT:
                    score += 0.05
                    reasons.append("Water-risk consideration: This drought-tolerant crop is well-suited for low-rainfall conditions.")
        except (ValueError, TypeError):
            pass
            
    # Check if weather forecast signals explicitly mention dry spells or heavy rain
    forecast_signals = weather_context.get("risk_signals", [])
    if forecast_signals and isinstance(forecast_signals, list):
        has_dry_spell = any(isinstance(s, str) and ("dry spell" in s.lower() or "drought" in s.lower()) for s in forecast_signals)
        has_heavy_rain = any(isinstance(s, str) and ("heavy rain" in s.lower() or "flood" in s.lower()) for s in forecast_signals)
        
        if has_dry_spell:
            if crop_lower in WATER_INTENSIVE:
                score -= 0.05
                reasons.append("Climate consideration: Forecasted dry spells make this water-intensive crop highly risky.")
            if crop_lower in DROUGHT_TOLERANT:
                score += 0.05
                reasons.append("Climate consideration: Drought-tolerant nature makes this crop resilient to forecasted dry spells.")
        
        if has_heavy_rain and crop_lower in DROUGHT_TOLERANT:
            score -= 0.03
            reasons.append("Climate consideration: This drought-tolerant crop may suffer from waterlogging due to forecasted heavy rains.")
            
    # 3. Satellite Vegetation (NDVI) Context
    ndvi_status = ndvi_context.get("status")
    if ndvi_status == "AVAILABLE":
        ndvi_val = ndvi_context.get("ndvi")
        if ndvi_val is not None:
            try:
                ndvi_val = float(ndvi_val)
                if ndvi_val < 0.2:
                    if crop_lower in LEGUMES:
                        score += 0.02
                        reasons.append("Satellite vegetation signal: Low vegetation index (NDVI < 0.2) detected. Nitrogen-fixing legumes are well-suited for early planting or establishing cover in sparse conditions.")
            except (ValueError, TypeError):
                pass
                
    # Bound the adjustment
    score = max(-0.15, min(0.15, score))
    
    return score, reasons

def apply_regenerative_ranking(
    crop_probabilities: List[Tuple[str, float]], 
    soil_context: Dict[str, float],
    weather_context: Dict[str, Any],
    ndvi_context: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Takes the baseline ML crop probabilities and applies the regenerative heuristic.
    Returns a sorted list of dictionaries with updated scores and reasons.
    """
    results = []
    
    for crop, base_prob in crop_probabilities:
        adj_score, reasons = calculate_regenerative_score(crop, soil_context, weather_context, ndvi_context, base_prob)
        final_score = base_prob + adj_score
        
        results.append({
            "crop": crop,
            "baseline_probability": float(base_prob),
            "regenerative_adjustment": float(adj_score),
            "final_score": float(final_score),
            "regenerative_reasons": reasons
        })
        
    # Sort by final score descending
    results.sort(key=lambda x: x["final_score"], reverse=True)
    return results
