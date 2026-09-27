import json
import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.cache import cache
from pydantic import ValidationError
from google import genai
from google.genai import types

from .schemas import AgriculturalObservation
from .prompt_builder import build_interop_prompt, get_interop_system_instruction
from predictions.ai.orchestrator import AIOrchestrator
from predictions.ai.errors import TransientAIError, PermanentAIError, AIConfigurationError

logger = logging.getLogger(__name__)

# Lightweight rate limiter
def is_rate_limited(ip_address: str, limit: int = 10, timeout: int = 60) -> bool:
    cache_key = f"ratelimit_interop_{ip_address}"
    requests = cache.get(cache_key, 0)
    if requests >= limit:
        return True
    cache.set(cache_key, requests + 1, timeout)
    return False

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

@csrf_exempt
@require_POST
def interop_advisory_view(request):
    ip_addr = get_client_ip(request)
    if is_rate_limited(ip_addr, limit=5, timeout=60): # 5 requests per minute
        return JsonResponse({
            "success": False,
            "status": "RATE_LIMITED",
            "message": "Too many requests. Please try again later."
        }, status=429)

    # 1. Parse JSON
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({
            "success": False,
            "status": "INVALID_SCHEMA",
            "message": "Agricultural context failed validation. Invalid JSON."
        }, status=400)

    # 2. Pydantic validation (Canonical schema)
    try:
        obs = AgriculturalObservation(**data)
    except ValidationError as e:
        # Don't expose python traceback, just the fact it failed schema validation
        return JsonResponse({
            "success": False,
            "status": "INVALID_SCHEMA",
            "message": "Agricultural context failed validation."
        }, status=400)

    if obs.schema_version != "1.0":
        return JsonResponse({
            "success": False,
            "status": "INVALID_SCHEMA",
            "message": "Unsupported schema_version."
        }, status=400)

    # Check language
    if obs.context.language not in ["en", "hi", "mr"]:
        return JsonResponse({
            "success": False,
            "status": "UNSUPPORTED_LANGUAGE",
            "message": f"Unsupported language: {obs.context.language}"
        }, status=400)

    # 3. Gemini Authentication
    # Removing direct API key check here so orchestrator handles it.

    # 4. Build Prompt
    prompt_text = build_interop_prompt(obs)
    system_instruction = get_interop_system_instruction()

    # 5. Call Gemini
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "summary": {"type": "STRING", "description": "Brief 2-sentence agricultural summary."},
            "crop_explanation": {"type": "STRING", "description": "Why this crop suits the current soil and weather, if applicable."},
            "weather_advice": {"type": "STRING", "description": "Immediate actions based on current/forecast weather."},
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

    try:
        orchestrator = AIOrchestrator()
        advisory_data, metadata = orchestrator.generate_advisory_with_fallback(
            prompt_text=prompt_text,
            system_instruction=system_instruction,
            response_schema=response_schema,
            temperature=0.2
        )
        
        # Identify model version if possible
        model_version = metadata.get("model_version", "unknown")
        provider = metadata.get("provider", "Unknown Provider")
            
        return JsonResponse({
            "success": True,
            "schema_version": "1.0",
            "advisory": advisory_data,
            "provenance": {
                "source_id": "krushisense_ai_advisory",
                "provider": provider,
                "freshness_category": "AI_GENERATED",
                "model_version": model_version
            }
        })

    except AIConfigurationError as e:
        logger.error(f"Interop Advisory Configuration Error: {str(e)}")
        return JsonResponse({
            "success": False,
            "status": "AI_UNAVAILABLE",
            "message": "AI advisory is currently unavailable."
        }, status=503)
    except TransientAIError as e:
        logger.error(f"Interop Advisory Transient Error: {str(e)}")
        return JsonResponse({
            "success": False,
            "status": "AI_UNAVAILABLE",
            "message": "AI advisory service failed."
        }, status=503)
    except PermanentAIError as e:
        logger.error(f"Interop Advisory Permanent Error: {str(e)}")
        return JsonResponse({
            "success": False,
            "status": "AI_INVALID_RESPONSE",
            "message": "AI returned malformed data or request was invalid."
        }, status=502)
