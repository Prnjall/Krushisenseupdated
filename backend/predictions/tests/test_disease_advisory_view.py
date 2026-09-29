import pytest
import json
import io
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from unittest.mock import patch, MagicMock
from django.test import Client
from django.core.cache import cache
from PIL import Image

from predictions.ai.errors import TransientAIError, PermanentAIError

pytestmark = pytest.mark.django_db

@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()

@pytest.fixture
def client():
    return Client(SERVER_NAME='localhost')

def get_base_payload(status="LOW_CONFIDENCE"):
    return {
        "language": "en",
        "crop": "apple",
        "diagnosis": {"status": status, "confidence": 0.45},
        "location": {"region": "Test"},
        "weather_current": {"status": "UNAVAILABLE"},
        "weather_forecast": {"status": "UNAVAILABLE"},
        "satellite": {"status": "UNAVAILABLE"}
    }

def create_dummy_image():
    img = Image.new("RGB", (100, 100), color="green")
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    return buffer.getvalue()

@pytest.fixture
def mock_orchestrator():
    with patch('predictions.views.AIOrchestrator') as mock_orch_class:
        mock_orch = MagicMock()
        mock_orch_class.return_value = mock_orch
        
        # Mock generate_advisory_with_fallback
        mock_orch.generate_advisory_with_fallback.return_value = (
            {"summary": "Text success"}, {"provider": "Mock", "model_version": "1"}
        )
        # Mock generate_vision_advisory_with_fallback
        mock_orch.generate_vision_advisory_with_fallback.return_value = (
            {"assessment_type": "AI-Assisted Visual Assessment", "possible_condition": "Apple Scab", "confidence_level": "Moderate", "visual_evidence": "Spots", "uncertainty_disclaimer": "Not a diagnosis", "recommended_next_step": "Test"},
            {"provider": "Mock Vision", "model_version": "1"}
        )
        
        yield mock_orch

def test_json_text_advisory_request(client, mock_orchestrator):
    """A. Existing JSON text advisory request remains unchanged"""
    payload = get_base_payload(status="DISEASE_DETECTED")
    response = client.post(
        '/api/disease-advisory',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["advisory"]["summary"] == "Text success"
    mock_orchestrator.generate_advisory_with_fallback.assert_called_once()
    mock_orchestrator.generate_vision_advisory_with_fallback.assert_not_called()

@patch('predictions.image_utils.preprocess_multimodal_image')
def test_valid_multipart_vision_request(mock_preprocess, client, mock_orchestrator):
    """B. Valid multipart vision request, C. Cross-crop/LOW_CONFIDENCE request, H. Vision orchestrator success"""
    mock_preprocess.return_value = (b"sanitized", "image/jpeg", {"width": 100, "height": 100})
    
    payload = get_base_payload(status="LOW_CONFIDENCE")
    img_bytes = create_dummy_image()
    
    # We must post multipart/form-data
    response = client.post(
        '/api/disease-advisory',
        data={
            'data': json.dumps(payload),
            'image': io.BytesIO(img_bytes)
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["advisory"]["assessment_type"] == "AI-Assisted Visual Assessment"
    
    mock_preprocess.assert_called_once()
    mock_orchestrator.generate_vision_advisory_with_fallback.assert_called_once()
    
    # L. No original image forwarding
    args, kwargs = mock_orchestrator.generate_vision_advisory_with_fallback.call_args
    assert kwargs['image_bytes'] == b"sanitized"
    assert "Apple Scab" in data["advisory"]["possible_condition"]

def test_disease_detected_with_image(client, mock_orchestrator):
    """D. Normal/DISEASE_DETECTED request with image is rejected or ignores vision (Currently rejects as invalid fallback)"""
    payload = get_base_payload(status="DISEASE_DETECTED")
    img_bytes = create_dummy_image()
    
    response = client.post(
        '/api/disease-advisory',
        data={
            'data': json.dumps(payload),
            'image': io.BytesIO(img_bytes)
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "Image provided but screening status does not warrant" in data["error"]

def test_missing_image_for_explicit_vision_request(client, mock_orchestrator):
    """E. Missing image for LOW_CONFIDENCE returns standard text error"""
    payload = get_base_payload(status="LOW_CONFIDENCE")
    
    response = client.post(
        '/api/disease-advisory',
        data=json.dumps(payload),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["advisory"] is None
    assert "uncertain or invalid" in data["message"]

def test_invalid_image(client):
    """F. Invalid image"""
    payload = get_base_payload(status="LOW_CONFIDENCE")
    response = client.post(
        '/api/disease-advisory',
        data={
            'data': json.dumps(payload),
            'image': io.BytesIO(b"not an image")
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "Invalid or corrupted image format" in data["error"]

def test_oversized_image(client):
    """G. >5 MB image"""
    payload = get_base_payload(status="LOW_CONFIDENCE")
    large_bytes = b"0" * (5 * 1024 * 1024 + 1)
    response = client.post(
        '/api/disease-advisory',
        data={
            'data': json.dumps(payload),
            'image': io.BytesIO(large_bytes)
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "exceeds the maximum limit" in data["error"]

def test_vision_provider_unavailable(client, mock_orchestrator):
    """I. Vision provider unavailable, K. No raw provider errors"""
    mock_orchestrator.generate_vision_advisory_with_fallback.side_effect = TransientAIError("Test raw exception")
    
    payload = get_base_payload(status="LOW_CONFIDENCE")
    img_bytes = create_dummy_image()
    
    response = client.post(
        '/api/disease-advisory',
        data={
            'data': json.dumps(payload),
            'image': io.BytesIO(img_bytes)
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "AI_UNAVAILABLE"
    assert "Test raw exception" not in data["message"]
    assert "temporarily unavailable" in data["message"]

def test_rate_limit(client):
    """J. Rate limit verification"""
    payload = get_base_payload(status="DISEASE_DETECTED")
    for _ in range(5):
        client.post(
            '/api/disease-advisory',
            data=json.dumps(payload),
            content_type='application/json',
            REMOTE_ADDR='10.0.0.10'
        )
        
    response = client.post(
        '/api/disease-advisory',
        data={
            'data': json.dumps(payload),
            'image': io.BytesIO(create_dummy_image())
        },
        REMOTE_ADDR='10.0.0.10'
    )
    assert response.status_code == 429
    data = response.json()
    assert data["status"] == "RATE_LIMITED"

