import pytest
import json
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from unittest.mock import patch, MagicMock
from django.test import Client, override_settings
from django.urls import reverse
from django.core.cache import cache

pytestmark = pytest.mark.django_db

@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()

@pytest.fixture
def client():
    return Client(SERVER_NAME='localhost')

@pytest.fixture
def mock_gemini():
    with patch('predictions.interoperability.views.genai.Client') as mock_client:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "summary": "Mock summary",
            "crop_explanation": "Mock explanation",
            "weather_advice": "Mock weather advice",
            "soil_advice": "Mock soil advice",
            "satellite_insight": "Mock satellite insight",
            "sustainable_practices": ["Mock practice"],
            "next_steps": ["Mock step"],
            "cautions": ["Mock caution"]
        })
        mock_response.model_version = "gemini-3.6-flash"
        mock_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_instance
        yield mock_client

def get_base_payload():
    return {
        "schema_version": "1.0",
        "context": {
            "language": "en",
            "region": "Test Region",
            "country": "Test Country"
        }
    }

def test_interop_api_valid_partial_context(client, mock_gemini, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    payload = get_base_payload()
    payload["soil"] = {
        "nitrogen": {"value": 50, "unit": "UNIT_NOT_VERIFIED", "source": "test"}
    }
    
    response = client.post(
        '/api/v1/interop/advisory/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["advisory"]["summary"] == "Mock summary"
    assert data["provenance"]["freshness_category"] == "AI_GENERATED"

def test_interop_api_invalid_json(client):
    response = client.post(
        '/api/v1/interop/advisory/',
        data="invalid json",
        content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()["status"] == "INVALID_SCHEMA"

def test_interop_api_invalid_schema_version(client):
    payload = get_base_payload()
    payload["schema_version"] = "2.0"
    response = client.post(
        '/api/v1/interop/advisory/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()["status"] == "INVALID_SCHEMA"

def test_interop_api_unsupported_language(client):
    payload = get_base_payload()
    payload["context"]["language"] = "fr"
    response = client.post(
        '/api/v1/interop/advisory/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()["status"] == "UNSUPPORTED_LANGUAGE"

def test_interop_api_missing_gemini_key(client, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post(
        '/api/v1/interop/advisory/',
        data=json.dumps(get_base_payload()),
        content_type='application/json'
    )
    assert response.status_code == 503
    assert response.json()["status"] == "AI_UNAVAILABLE"

def test_interop_api_pydantic_validation_error(client):
    payload = get_base_payload()
    payload["satellite"] = {
        "value": 5.0, # invalid NDVI
        "observed_at": "2026-08-20T12:00:00Z",
        "source": "test",
        "days_since_observation": 1
    }
    response = client.post(
        '/api/v1/interop/advisory/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 400
    assert response.json()["status"] == "INVALID_SCHEMA"

def test_interop_api_gemini_failure(client, mock_gemini, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    mock_gemini.return_value.models.generate_content.side_effect = Exception("API Error")
    
    response = client.post(
        '/api/v1/interop/advisory/',
        data=json.dumps(get_base_payload()),
        content_type='application/json'
    )
    assert response.status_code == 503
    assert response.json()["status"] == "AI_UNAVAILABLE"

def test_interop_api_gemini_malformed_json(client, mock_gemini, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    mock_gemini.return_value.models.generate_content.return_value.text = "invalid json response"
    
    response = client.post(
        '/api/v1/interop/advisory/',
        data=json.dumps(get_base_payload()),
        content_type='application/json'
    )
    assert response.status_code == 502
    assert response.json()["status"] == "AI_INVALID_RESPONSE"

def test_gps_coordinates_never_logged(client, mock_gemini, monkeypatch, caplog):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    payload = get_base_payload()
    payload["context"]["lat"] = 12.34
    payload["context"]["lon"] = 56.78
    
    response = client.post(
        '/api/v1/interop/advisory/',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert "12.34" not in caplog.text
    assert "56.78" not in caplog.text


# ==============================
# Rate-limit regression tests for browser-facing advisory endpoints
# ==============================

def _mock_agri_advisory_gemini():
    """Shared mock factory for predictions.views Gemini client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        "summary": "mock", "crop_explanation": "mock", "weather_advice": "mock",
        "soil_advice": "mock", "satellite_insight": "mock",
        "sustainable_practices": [], "next_steps": [], "cautions": []
    })
    mock_client.return_value.models.generate_content.return_value = mock_response
    return patch('predictions.views.genai.Client', mock_client)


def _agri_payload():
    return {
        "language": "en",
        "location": {"region": "Test"},
        "soil": {"N": 90, "P": 42, "K": 43, "pH": 6.5},
        "environment": {"temperature": 25, "humidity": 65, "rainfall_annual": 200},
        "weather_current": {},
        "weather_forecast": {"status": "UNAVAILABLE"},
        "satellite": {"status": "UNAVAILABLE"},
        "prediction": {
            "primary_crop": "rice",
            "top3": [{"crop": "rice", "prob": 0.85}],
            "familiarity": "high",
            "prediction_status": "high_confidence"
        }
    }


def _disease_payload():
    return {
        "language": "en",
        "crop": "apple",
        "diagnosis": {"status": "HEALTHY"},
        "location": {"region": "Test"},
        "weather_current": {"status": "UNAVAILABLE"},
        "weather_forecast": {"status": "UNAVAILABLE"},
        "satellite": {"status": "UNAVAILABLE"}
    }


@pytest.mark.django_db
def test_agri_advisory_rate_limit(client, monkeypatch):
    """After 5 requests from the same IP, the 6th must receive HTTP 429."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    with _mock_agri_advisory_gemini():
        for i in range(5):
            resp = client.post(
                '/api/agri-advisory',
                data=json.dumps(_agri_payload()),
                content_type='application/json',
                REMOTE_ADDR='10.0.0.1'
            )
            # First 5 requests must not be rate-limited
            assert resp.status_code != 429, f"Request {i+1} was unexpectedly rate-limited"

        # 6th request from the same IP must be rejected
        resp = client.post(
            '/api/agri-advisory',
            data=json.dumps(_agri_payload()),
            content_type='application/json',
            REMOTE_ADDR='10.0.0.1'
        )
        assert resp.status_code == 429
        data = resp.json()
        assert data["success"] is False
        assert data["status"] == "RATE_LIMITED"
        assert "message" in data


@pytest.mark.django_db
def test_agri_advisory_rate_limit_different_ips(client, monkeypatch):
    """Rate-limit is per-IP: a second IP must be unaffected by the first IP's counter."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    with _mock_agri_advisory_gemini():
        # Exhaust the limit for IP A
        for _ in range(5):
            client.post(
                '/api/agri-advisory',
                data=json.dumps(_agri_payload()),
                content_type='application/json',
                REMOTE_ADDR='10.0.0.2'
            )

        # IP B must still be served
        resp = client.post(
            '/api/agri-advisory',
            data=json.dumps(_agri_payload()),
            content_type='application/json',
            REMOTE_ADDR='10.0.0.3'
        )
        assert resp.status_code != 429


@pytest.mark.django_db
def test_disease_advisory_rate_limit(client, monkeypatch):
    """After 5 requests from the same IP, the 6th must receive HTTP 429."""
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    with _mock_agri_advisory_gemini():
        for i in range(5):
            resp = client.post(
                '/api/disease-advisory',
                data=json.dumps(_disease_payload()),
                content_type='application/json',
                REMOTE_ADDR='10.0.0.4'
            )
            assert resp.status_code != 429, f"Request {i+1} was unexpectedly rate-limited"

        resp = client.post(
            '/api/disease-advisory',
            data=json.dumps(_disease_payload()),
            content_type='application/json',
            REMOTE_ADDR='10.0.0.4'
        )
        assert resp.status_code == 429
        data = resp.json()
        assert data["success"] is False
        assert data["status"] == "RATE_LIMITED"
        assert "message" in data


@pytest.mark.django_db
def test_advisory_and_interop_rate_limits_are_independent(client, monkeypatch):
    """
    Exhausting the advisory quota for an IP must NOT consume its interop quota,
    and vice versa — the cache namespaces are separate.
    """
    monkeypatch.setenv("GEMINI_API_KEY", "test_key")
    interop_payload = {
        "schema_version": "1.0",
        "context": {"language": "en", "region": "Test", "country": "India"}
    }
    with _mock_agri_advisory_gemini():
        with patch('predictions.interoperability.views.genai.Client') as mock_interop:
            mock_interop_resp = MagicMock()
            mock_interop_resp.text = json.dumps({
                "summary": "mock", "crop_explanation": "mock", "weather_advice": "mock",
                "soil_advice": "mock", "satellite_insight": "mock",
                "sustainable_practices": [], "next_steps": [], "cautions": []
            })
            mock_interop_resp.model_version = "gemini-3.6-flash"
            mock_interop.return_value.models.generate_content.return_value = mock_interop_resp

            ip = '10.0.0.5'

            # Exhaust advisory quota
            for _ in range(5):
                client.post(
                    '/api/agri-advisory',
                    data=json.dumps(_agri_payload()),
                    content_type='application/json',
                    REMOTE_ADDR=ip
                )

            # Advisory must now be blocked
            resp = client.post(
                '/api/agri-advisory',
                data=json.dumps(_agri_payload()),
                content_type='application/json',
                REMOTE_ADDR=ip
            )
            assert resp.status_code == 429

            # Interop must still be accessible (separate namespace)
            resp = client.post(
                '/api/v1/interop/advisory/',
                data=json.dumps(interop_payload),
                content_type='application/json',
                REMOTE_ADDR=ip
            )
            assert resp.status_code != 429
